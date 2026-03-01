# 📊 Monitoring & Observability Stack - Technical Debt

> **Status**: 🔴 **NOT IMPLEMENTED** - Critical for production readiness  
> **Priority**: 🔥 **HIGH** - Required for 24/7 bastion operation  
> **Estimated Effort**: 2-3 weeks (40-60 hours)  
> **Dependencies**: PKI infrastructure ✅, Docker ✅, mTLS patterns ✅

---

## 📋 Executive Summary

**Problem**: No visibility into infrastructure health, performance, or security events.

**Solution**: Deploy a full observability stack (LGTM + OTEL) on Bastion for 24/7 monitoring.

**Impact**:
- ✅ Proactive issue detection (disk full, high CPU, service crashes)
- ✅ Security monitoring (failed auth, firewall blocks, cert issues)
- ✅ Performance insights (request latency, bottlenecks)
- ✅ Troubleshooting capabilities (logs, traces, metrics correlation)
- ✅ GPU monitoring for AI workload visibility

---

## 🎯 Goals

### Primary Goals
1. **24/7 Infrastructure Monitoring** - CPU, RAM, Disk, Network on all hosts
2. **Service Health Tracking** - Uptime, performance, error rates for all services
3. **Security Event Monitoring** - SSH attempts, firewall blocks, cert validation failures
4. **GPU Monitoring** - Utilization, temperature, memory for Monster workstation
5. **Centralized Logging** - Aggregate logs from all hosts for debugging
6. **mTLS Protection** - All monitoring endpoints protected with mutual TLS

### Secondary Goals
7. **Distributed Tracing** - Request flow visualization (when K8s deployed)
8. **Alerting** - Automated notifications for critical events
9. **Capacity Planning** - Historical data for resource forecasting
10. **SLA Tracking** - Service uptime and availability metrics

---

## 🏗️ Architecture

### Technology Stack

| Component | Version | Purpose | Why This Choice |
|-----------|---------|---------|----------------|
| **Prometheus** | v2.48.0 | Metrics storage & querying | Industry standard, huge ecosystem |
| **Grafana** | v10.2.3 | Visualization & dashboards | Best-in-class UI, multi-datasource |
| **Loki** | v2.9.3 | Log aggregation | Native Grafana integration, label-based |
| **Tempo** | v2.3.1 | Distributed tracing | Grafana native, works with OTEL |
| **Grafana Alloy** | v1.0.0 | Telemetry collection | Modern replacement for Grafana Agent |
| **OTEL Collector** | v0.91.0 | Standards-based telemetry | Future-proof, vendor-neutral |
| **node_exporter** | v1.7.0 | System metrics | Standard Prometheus exporter |
| **cAdvisor** | v0.47.2 | Container metrics | Docker-native, comprehensive |
| **nvidia_gpu_exporter** | latest | GPU metrics | NVIDIA-specific monitoring |

### Deployment Location

**Bastion Gateway** - Rationale:
- ✅ 24/7 uptime requirement
- ✅ Always-on for remote monitoring access
- ✅ Central point for data aggregation
- ✅ Sufficient resources (< 1 core, ~1.5GB RAM)
- ✅ Already running critical services

### Network Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BASTION (24/7 Monitoring Hub)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Grafana (Port 8443 via GhostTunnel)                          │ │
│  │  - Unified dashboard interface                                │ │
│  │  - mTLS client cert authentication                            │ │
│  │  - Access: https://grafana.lab                               │ │
│  └───────────┬─────────────┬─────────────┬─────────────┬─────────┘ │
│              │             │             │             │            │
│     ┌────────▼──────┐ ┌────▼──────┐ ┌───▼──────┐ ┌───▼──────┐    │
│     │  Prometheus   │ │   Loki    │ │  Tempo   │ │ AlertMgr │    │
│     │  (Metrics)    │ │  (Logs)   │ │ (Traces) │ │ (Alerts) │    │
│     │  :9090        │ │  :3100    │ │  :3200   │ │  :9093   │    │
│     └────────▲──────┘ └────▲──────┘ └───▲──────┘ └───▲──────┘    │
│              │             │             │             │            │
│     ┌────────┴─────────────┴─────────────┴─────────────┴────────┐  │
│     │  Grafana Alloy (Central Collector)                        │  │
│     │  - OTLP receiver: :4317 (gRPC), :4318 (HTTP)             │  │
│     │  - Prometheus scraper (local exporters)                   │  │
│     │  - Log processor & forwarder                              │  │
│     │  - mTLS for all external connections                      │  │
│     └────────▲──────────────────────────────────────────────────┘  │
│              │                                                      │
│     ┌────────┴──────────┐  ┌──────────────┐  ┌─────────────────┐  │
│     │  node_exporter    │  │  cAdvisor    │  │  Traefik        │  │
│     │  (System Metrics) │  │ (Containers) │  │  (HTTP Metrics) │  │
│     │  :9100            │  │  :8080       │  │  :8082          │  │
│     └───────────────────┘  └──────────────┘  └─────────────────┘  │
│                                                                     │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                  ┌───────────────┼───────────────┐
                  │               │               │
       ┌──────────▼──────┐ ┌──────▼──────┐ ┌─────▼───────────┐
       │   Workstation   │ │  K8s Cluster│ │  Future Hosts   │
       │   (Monster)     │ │   (Planned) │ │                 │
       └──────────┬──────┘ └──────┬──────┘ └─────┬───────────┘
                  │               │               │
       ┌──────────▼───────────────▼───────────────▼───────────┐
       │  OTEL Collectors (Per-Host Agents)                   │
       │  - Application instrumentation (traces, metrics)     │
       │  - Log collection (journald, containers)             │
       │  - System metrics (node_exporter)                    │
       │  - GPU metrics (nvidia_gpu_exporter on Monster)      │
       │  - Forward to Grafana Alloy via mTLS                 │
       └──────────────────────────────────────────────────────┘
```

### Data Flow

```
┌─────────────┐
│ Application │
└──────┬──────┘
       │ (instrumented with OTEL SDK)
       ↓
┌──────────────────┐
│ OTEL Collector   │ (per-host agent)
│ - Receives OTLP  │
│ - Processes data │
│ - Batches        │
└────────┬─────────┘
         │ mTLS (OTLP/gRPC)
         ↓
┌─────────────────────┐
│  Grafana Alloy      │ (central on Bastion)
│  - Aggregates       │
│  - Enriches labels  │
│  - Routes by type   │
└──┬────────┬─────┬───┘
   │        │     │
   │Metrics │Logs │Traces
   ↓        ↓     ↓
┌────┐  ┌────┐  ┌─────┐
│Prom│  │Loki│  │Tempo│
└────┘  └────┘  └─────┘
   │        │     │
   └────────┴─────┴─────→ Grafana Dashboards
```

---

## 📦 Implementation Plan

### Phase 1: Foundation (Week 1)

**Goal**: Basic system monitoring operational

#### Tasks:
- [ ] Create `roles/monitoring/` Ansible role
- [ ] Generate PKI certificates for monitoring services
- [ ] Deploy Prometheus + node_exporter
- [ ] Deploy Grafana with mTLS via GhostTunnel
- [ ] Configure firewall rules for monitoring ports
- [ ] Import Node Exporter Full dashboard (ID: 1860)
- [ ] Set up basic alerts (host down, disk full, high CPU)

#### Deliverables:
```yaml
✅ Prometheus scraping Bastion metrics
✅ Grafana accessible at https://grafana.lab (mTLS)
✅ Dashboard showing CPU, RAM, Disk, Network
✅ Alert on critical conditions
```

#### Acceptance Criteria:
- Can view real-time CPU usage in Grafana
- Alert fires when disk usage > 90%
- All connections use mTLS
- Metrics retained for 30 days

---

### Phase 2: Container & Service Metrics (Week 2)

**Goal**: Full visibility into Docker services

#### Tasks:
- [ ] Deploy cAdvisor on all Docker hosts
- [ ] Configure Prometheus to scrape cAdvisor
- [ ] Add Traefik metrics endpoint scraping
- [ ] Deploy nvidia_gpu_exporter on Monster
- [ ] Create container health dashboard
- [ ] Create service performance dashboard
- [ ] Set up alerts for container restarts
- [ ] Add GPU temperature/utilization alerts

#### Deliverables:
```yaml
✅ Container CPU/RAM metrics per service
✅ GPU metrics (utilization, temp, memory) on Monster
✅ Traefik request rate & latency metrics
✅ Dashboard showing all running containers
✅ Alert on container crash/restart
```

#### Acceptance Criteria:
- Can identify which container uses most CPU
- GPU temperature visible in real-time
- Alert fires on GPU temp > 85°C
- Traefik 4xx/5xx error rate tracked

---

### Phase 3: Log Aggregation (Week 3)

**Goal**: Centralized logging for debugging & security

#### Tasks:
- [ ] Deploy Loki on Bastion
- [ ] Configure Grafana Alloy log collection
- [ ] Collect journald logs (systemd services)
- [ ] Collect Docker container logs
- [ ] Collect firewall logs (firewalld)
- [ ] Collect SSH authentication logs
- [ ] Create security dashboard (failed logins, firewall blocks)
- [ ] Create log explorer dashboard
- [ ] Set up log-based alerts (SSH brute force, cert errors)

#### Deliverables:
```yaml
✅ All system logs searchable in Grafana
✅ Container logs aggregated by service
✅ Security events dashboard
✅ Alert on SSH login failures > 5/min
✅ Logs retained for 30 days
```

#### Acceptance Criteria:
- Can search logs for "failed password" across all hosts
- Failed SSH attempts visible in dashboard
- Firewall block events tracked
- Log correlation with metrics (e.g., CPU spike + error logs)

---

### Phase 4: Unified Telemetry Pipeline (Week 4)

**Goal**: Production-grade observability with OTEL

#### Tasks:
- [ ] Deploy Grafana Alloy on Bastion
- [ ] Configure OTLP receivers (gRPC + HTTP)
- [ ] Migrate Prometheus scraping to Alloy
- [ ] Configure log forwarding to Loki
- [ ] Deploy OTEL collectors on remote hosts
- [ ] Configure mTLS for all collector connections
- [ ] Test end-to-end pipeline (app → OTEL → Alloy → Prometheus)
- [ ] Create pipeline health dashboard
- [ ] Document OTEL instrumentation guide

#### Deliverables:
```yaml
✅ Grafana Alloy as central telemetry hub
✅ OTEL collectors on all hosts
✅ mTLS-protected OTLP endpoints
✅ Unified collection pipeline
✅ Documentation for adding new services
```

#### Acceptance Criteria:
- Remote hosts send metrics via OTLP over mTLS
- Pipeline latency < 10 seconds (data ingestion to query)
- No data loss during network interruptions (buffering works)
- Clear documentation for instrumenting new apps

---

### Phase 5: Distributed Tracing (Post-K8s)

**Goal**: Request-level observability across services

#### Tasks:
- [ ] Deploy Tempo on Bastion
- [ ] Configure Grafana Alloy to forward traces to Tempo
- [ ] Instrument sample application with OTEL SDK
- [ ] Test trace collection end-to-end
- [ ] Create trace visualization dashboard
- [ ] Configure trace sampling (1% for high-volume services)
- [ ] Set up trace-based alerts (latency SLOs)
- [ ] Document microservice tracing patterns

#### Deliverables:
```yaml
✅ Tempo storing traces
✅ Sample app sending traces
✅ Dashboard showing request flow
✅ Latency breakdown by service
✅ Trace correlation with logs/metrics
```

#### Acceptance Criteria:
- Can view full request trace: Traefik → GhostTunnel → App → DB
- Identify slowest span in request chain
- Click from trace to related logs
- Trace retention 30 days

---

### Phase 6: Advanced Alerting (Ongoing)

**Goal**: Proactive issue detection and notifications

#### Tasks:
- [ ] Deploy AlertManager
- [ ] Configure Slack/Discord/Email integration
- [ ] Define critical alerts (host down, service down, disk full)
- [ ] Define warning alerts (high load, cert expiry, performance degradation)
- [ ] Set up alert routing (critical → pager, warning → email)
- [ ] Configure alert silencing/maintenance windows
- [ ] Create runbooks for common alerts
- [ ] Test alert delivery end-to-end

#### Deliverables:
```yaml
✅ AlertManager operational
✅ Notifications to Slack/Discord
✅ Critical vs warning alert separation
✅ Runbooks for each alert type
✅ Alert testing procedure
```

#### Acceptance Criteria:
- Receive notification within 1 minute of host down
- Alerts include runbook link
- Can silence alerts during maintenance
- No alert fatigue (< 5 alerts/day normal operations)

---

## 🔐 mTLS Integration

### Certificate Requirements

All monitoring components require mTLS certificates:

```yaml
# PKI Services to Add (roles/pki/vars/main.yml)
pki_services:
  # Monitoring Core
  - name: prometheus
    dns_names: [prometheus.lab, bastion.lab]
    ip_addresses: [192.168.1.10]  # Bastion IP
    
  - name: grafana
    dns_names: [grafana.lab, bastion.lab]
    ip_addresses: [192.168.1.10]
    
  - name: loki
    dns_names: [loki.lab, bastion.lab]
    ip_addresses: [192.168.1.10]
    
  - name: tempo
    dns_names: [tempo.lab, bastion.lab]
    ip_addresses: [192.168.1.10]
    
  - name: alertmanager
    dns_names: [alertmanager.lab, bastion.lab]
    ip_addresses: [192.168.1.10]
    
  - name: alloy
    dns_names: [alloy.lab, bastion.lab]
    ip_addresses: [192.168.1.10]

# Exporters (per-host)
pki_exporter_services:
  - name: node-exporter-bastion
    dns_names: [bastion.lab]
    ip_addresses: [192.168.1.10]
    
  - name: node-exporter-monster
    dns_names: [monster.lab]
    ip_addresses: [192.168.1.20]
    
  - name: cadvisor-bastion
    dns_names: [bastion.lab]
    ip_addresses: [192.168.1.10]
    
  - name: cadvisor-monster
    dns_names: [monster.lab]
    ip_addresses: [192.168.1.20]
    
  - name: nvidia-exporter-monster
    dns_names: [monster.lab]
    ip_addresses: [192.168.1.20]

# Client Certificates
pki_monitoring_clients:
  - name: prometheus-scraper  # For scraping exporters
  - name: alloy-collector     # For receiving OTLP
  - name: otel-forwarder      # For sending to Alloy
```

### mTLS Patterns

#### 1. GhostTunnel for User Access
```yaml
# Grafana accessible via mTLS
grafana_ghosttunnel:
  image: ghostunnel/ghostunnel:v1.8.4-alpine
  command:
    - server
    - --listen=0.0.0.0:8443
    - --target=127.0.0.1:3000
    - --cert=/etc/certs/grafana.crt
    - --key=/etc/certs/grafana.key
    - --cacert=/etc/certs/ca.crt
    - --allow-all  # Any valid client cert
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.grafana.rule=Host(`grafana.lab`)"
```

#### 2. Prometheus Scraping with mTLS
```yaml
# Prometheus config (prometheus.yml)
scrape_configs:
  - job_name: 'node'
    scheme: https
    tls_config:
      cert_file: /etc/certs/prometheus-scraper.crt
      key_file: /etc/certs/prometheus-scraper.key
      ca_file: /etc/certs/ca.crt
    static_configs:
      - targets: ['bastion.lab:9100', 'monster.lab:9100']
```

#### 3. OTLP with mTLS
```yaml
# Grafana Alloy OTLP receiver
otelcol.receiver.otlp "default" {
  grpc {
    endpoint = "0.0.0.0:4317"
    tls {
      cert_file = "/etc/certs/alloy-server.crt"
      key_file = "/etc/certs/alloy-server.key"
      ca_file = "/etc/certs/ca.crt"
      client_ca_file = "/etc/certs/ca.crt"
      client_auth_type = "RequireAndVerifyClientCert"
    }
  }
}

# OTEL Collector exporter (on remote hosts)
exporters:
  otlp:
    endpoint: bastion.lab:4317
    tls:
      cert_file: /etc/certs/otel-forwarder.crt
      key_file: /etc/certs/otel-forwarder.key
      ca_file: /etc/certs/ca.crt
```

---

## 📊 Dashboards & Visualizations

### Essential Dashboards

#### 1. Infrastructure Overview
```yaml
Name: "Homelab Infrastructure"
Refresh: 30s
Variables:
  - host: [bastion, monster, k8s-node-*]
  - interval: [1m, 5m, 15m, 1h]

Panels:
  Row 1: System Status
    - Host Uptime (stat)
    - CPU Usage % (gauge)
    - Memory Usage % (gauge)
    - Disk Usage % (gauge)
  
  Row 2: Resource Trends
    - CPU Usage Over Time (graph)
    - Memory Usage Over Time (graph)
    - Disk I/O (graph)
    - Network Traffic (graph)
  
  Row 3: Load & Temperature
    - System Load 1m/5m/15m (graph)
    - CPU Temperature (graph)
    - Disk Temperature (graph)
```

#### 2. GPU Monitoring (Monster)
```yaml
Name: "GPU Workstation - Monster"
Refresh: 10s

Panels:
  Row 1: GPU Overview
    - GPU Utilization % (gauge)
    - GPU Memory Usage (gauge)
    - GPU Temperature °C (gauge)
    - GPU Power Draw W (gauge)
  
  Row 2: GPU Trends
    - GPU Utilization Over Time (graph)
    - GPU Memory Usage Over Time (graph)
    - GPU Temperature Over Time (graph)
    - GPU Power Consumption (graph)
  
  Row 3: GPU Details
    - CUDA Version (stat)
    - Driver Version (stat)
    - GPU Clock Speed (graph)
    - Memory Clock Speed (graph)
  
  Row 4: Workload Analysis
    - Running Processes (table)
    - Process Memory Usage (table)
```

#### 3. Container Health
```yaml
Name: "Docker Containers"
Refresh: 30s

Panels:
  Row 1: Container Overview
    - Total Containers (stat)
    - Running Containers (stat)
    - Stopped Containers (stat)
    - Container Restarts (stat)
  
  Row 2: Resource Usage
    - Container CPU % (bar chart)
    - Container Memory Usage (bar chart)
    - Container Network I/O (graph)
    - Container Disk I/O (graph)
  
  Row 3: Container Details
    - Container Status Table (table)
      Columns: Name | Status | CPU% | Memory | Uptime | Restarts
```

#### 4. Service Performance
```yaml
Name: "Service Performance"
Refresh: 30s
Variables:
  - service: [traefik, adguard, upsnap, memos, sure-finance]

Panels:
  Row 1: HTTP Metrics (Traefik)
    - Requests/sec (stat)
    - Avg Response Time (stat)
    - Error Rate % (stat)
    - Backend Status (stat)
  
  Row 2: Request Analysis
    - Request Rate by Service (graph)
    - Response Time P50/P95/P99 (graph)
    - HTTP Status Codes (pie chart)
    - Request Duration Heatmap (heatmap)
  
  Row 3: Backend Health
    - Backend Availability (graph)
    - Active Connections (graph)
    - Request Queue Depth (graph)
```

#### 5. Security Dashboard
```yaml
Name: "Security Events"
Refresh: 1m

Panels:
  Row 1: Authentication
    - SSH Login Attempts (stat)
    - Failed SSH Logins (stat)
    - Active SSH Sessions (stat)
  
  Row 2: Firewall Activity
    - Firewall Blocks/min (graph)
    - Blocks by Zone (pie chart)
    - Top Blocked IPs (table)
    - Block Reasons (table)
  
  Row 3: Certificate Security
    - Cert Validation Failures (stat)
    - Certs Expiring <30 Days (table)
    - mTLS Connection Rate (graph)
  
  Row 4: Recent Security Events (Logs)
    - Failed Login Attempts (logs)
    - Firewall Blocks (logs)
    - Suspicious Activity (logs)
```

#### 6. Log Explorer
```yaml
Name: "Log Explorer"
Refresh: 10s

Panels:
  - Log Stream (logs panel)
    Filters:
      - hostname: [bastion, monster]
      - service: [sshd, firewalld, docker, traefik, etc.]
      - level: [error, warning, info, debug]
    
  - Log Volume Over Time (graph)
  - Error Rate by Service (graph)
  - Top Log Sources (table)
```

---

## 🚨 Alert Rules

### Critical Alerts (Immediate Response)

```yaml
groups:
  - name: critical_infrastructure
    interval: 30s
    rules:
      # Host Availability
      - alert: HostDown
        expr: up{job="node"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Host {{ $labels.instance }} is down"
          description: "{{ $labels.instance }} has been unreachable for 1 minute"
          runbook: https://wiki.lab/runbooks/host-down
      
      # Disk Space
      - alert: DiskFull
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk almost full on {{ $labels.instance }}"
          description: "Disk usage is {{ $value | humanize }}% on {{ $labels.instance }}"
          runbook: https://wiki.lab/runbooks/disk-full
      
      # Memory Exhaustion
      - alert: OutOfMemory
        expr: (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 < 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Memory critically low on {{ $labels.instance }}"
          description: "Only {{ $value | humanize }}% memory available"
          runbook: https://wiki.lab/runbooks/out-of-memory
      
      # CPU Overload
      - alert: HighCPU
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value | humanize }}% for 10 minutes"
          runbook: https://wiki.lab/runbooks/high-cpu
      
      # Service Down
      - alert: ServiceDown
        expr: up{job=~"traefik|adguard|grafana|prometheus"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Critical service {{ $labels.job }} is down"
          description: "{{ $labels.job }} on {{ $labels.instance }} is unreachable"
          runbook: https://wiki.lab/runbooks/service-down

  - name: critical_gpu
    interval: 30s
    rules:
      # GPU Temperature
      - alert: GPUOverheating
        expr: nvidia_gpu_temperature_celsius > 85
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "GPU overheating on {{ $labels.instance }}"
          description: "GPU temperature is {{ $value }}°C (threshold: 85°C)"
          runbook: https://wiki.lab/runbooks/gpu-overheat
      
      # GPU Memory
      - alert: GPUMemoryFull
        expr: (nvidia_gpu_memory_used_bytes / nvidia_gpu_memory_total_bytes) * 100 > 95
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "GPU memory exhausted on {{ $labels.instance }}"
          description: "GPU memory usage is {{ $value | humanize }}%"
          runbook: https://wiki.lab/runbooks/gpu-memory-full

  - name: critical_security
    interval: 30s
    rules:
      # SSH Brute Force
      - alert: SSHBruteForce
        expr: rate(sshd_failed_logins_total[5m]) > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Possible SSH brute force on {{ $labels.instance }}"
          description: "{{ $value | humanize }} failed SSH attempts per minute"
          runbook: https://wiki.lab/runbooks/ssh-brute-force
      
      # Certificate Expiry
      - alert: CertificateExpiring
        expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 7
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Certificate expiring soon for {{ $labels.instance }}"
          description: "Certificate expires in {{ $value | humanize }} days"
          runbook: https://wiki.lab/runbooks/cert-renewal
```

### Warning Alerts (Monitor & Plan)

```yaml
groups:
  - name: warning_infrastructure
    interval: 1m
    rules:
      # High Load
      - alert: HighLoad
        expr: node_load15 > 4
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High system load on {{ $labels.instance }}"
          description: "15-minute load average is {{ $value }}"
      
      # Disk Space Warning
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 20
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Disk space running low on {{ $labels.instance }}"
          description: "Only {{ $value | humanize }}% disk space remaining"
      
      # Container Restarts
      - alert: ContainerRestarting
        expr: rate(container_restarts_total[15m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container {{ $labels.name }} restarting frequently"
          description: "Container has restarted {{ $value }} times in 15 minutes"
      
      # High Network Traffic
      - alert: HighNetworkTraffic
        expr: rate(node_network_receive_bytes_total[5m]) > 100000000  # 100MB/s
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High network traffic on {{ $labels.instance }}"
          description: "Network receive rate is {{ $value | humanize }}B/s"
```

---

## 💾 Resource Requirements

### Storage Estimates (30-day retention)

```yaml
Prometheus:
  Metrics per second: ~5000
  Storage per sample: ~2 bytes (compressed)
  Daily storage: ~5000 * 86400 * 2 = ~864MB/day
  30-day retention: ~25GB
  Recommended: 50GB volume (headroom for growth)

Loki:
  Log lines per second: ~100
  Avg line size: ~200 bytes
  Daily storage: ~100 * 86400 * 200 = ~1.7GB/day
  30-day retention: ~50GB (with compression)
  Recommended: 100GB volume

Tempo:
  Traces per second: ~10 (after K8s deployment)
  Avg trace size: ~50KB
  Daily storage: ~10 * 86400 * 50KB = ~43GB/day
  30-day retention: ~1.3TB (impractical!)
  Recommendation: 7-day retention = ~300GB
  Or: 1% sampling = ~13GB for 30 days

Grafana:
  Dashboards + config: ~100MB
  SQLite database: ~500MB
  Total: ~1GB

Total Storage (Bastion):
  - Prometheus: 50GB
  - Loki: 100GB
  - Tempo: 20GB (7-day, 1% sampling)
  - Grafana: 1GB
  - Total: ~171GB
```

### CPU & Memory (Bastion)

```yaml
Prometheus:
  CPU: 200-400m (0.2-0.4 cores)
  RAM: 500MB-1GB

Grafana:
  CPU: 100m
  RAM: 200MB

Loki:
  CPU: 150m
  RAM: 300-500MB

Tempo:
  CPU: 100m (minimal until K8s)
  RAM: 200MB

Grafana Alloy:
  CPU: 150-300m
  RAM: 250-500MB

AlertManager:
  CPU: 50m
  RAM: 100MB

Exporters (per-host):
  node_exporter: CPU 50m, RAM 50MB
  cAdvisor: CPU 100m, RAM 150MB
  nvidia_exporter: CPU 50m, RAM 50MB

Total (Bastion):
  CPU: ~1 core (1000m)
  RAM: ~2.5GB
  Comfortable for modern server
```

---

## 🔧 Configuration Files

### 1. Prometheus Configuration

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'homelab'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

# Rule files
rule_files:
  - '/etc/prometheus/rules/*.yml'

# Scrape configurations
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  # Node Exporter (system metrics)
  - job_name: 'node'
    scheme: https
    tls_config:
      cert_file: /etc/certs/prometheus-scraper.crt
      key_file: /etc/certs/prometheus-scraper.key
      ca_file: /etc/certs/ca.crt
    static_configs:
      - targets:
          - bastion.lab:9100
          - monster.lab:9100
        labels:
          env: 'production'
  
  # cAdvisor (container metrics)
  - job_name: 'cadvisor'
    scheme: https
    tls_config:
      cert_file: /etc/certs/prometheus-scraper.crt
      key_file: /etc/certs/prometheus-scraper.key
      ca_file: /etc/certs/ca.crt
    static_configs:
      - targets:
          - bastion.lab:8080
          - monster.lab:8080
  
  # NVIDIA GPU Exporter (Monster only)
  - job_name: 'nvidia_gpu'
    scheme: https
    tls_config:
      cert_file: /etc/certs/prometheus-scraper.crt
      key_file: /etc/certs/prometheus-scraper.key
      ca_file: /etc/certs/ca.crt
    static_configs:
      - targets:
          - monster.lab:9835
        labels:
          hostname: 'monster'
  
  # Traefik (HTTP metrics)
  - job_name: 'traefik'
    scheme: https
    tls_config:
      cert_file: /etc/certs/prometheus-scraper.crt
      key_file: /etc/certs/prometheus-scraper.key
      ca_file: /etc/certs/ca.crt
    static_configs:
      - targets:
          - bastion.lab:8082

# Storage configuration
storage:
  tsdb:
    path: /prometheus
    retention:
      time: 30d
      size: 45GB
```

### 2. Grafana Alloy Configuration

```hcl
// config.alloy - Grafana Alloy configuration

// OTLP Receiver (for remote collectors)
otelcol.receiver.otlp "default" {
  grpc {
    endpoint = "0.0.0.0:4317"
    
    tls {
      cert_file = "/etc/certs/alloy-server.crt"
      key_file  = "/etc/certs/alloy-server.key"
      ca_file   = "/etc/certs/ca.crt"
      client_ca_file = "/etc/certs/ca.crt"
      client_auth_type = "RequireAndVerifyClientCert"
    }
  }
  
  http {
    endpoint = "0.0.0.0:4318"
    
    tls {
      cert_file = "/etc/certs/alloy-server.crt"
      key_file  = "/etc/certs/alloy-server.key"
      ca_file   = "/etc/certs/ca.crt"
      client_ca_file = "/etc/certs/ca.crt"
      client_auth_type = "RequireAndVerifyClientCert"
    }
  }
  
  output {
    metrics = [otelcol.processor.batch.default.input]
    logs    = [otelcol.processor.batch.default.input]
    traces  = [otelcol.processor.batch.default.input]
  }
}

// Batch Processor (efficiency)
otelcol.processor.batch "default" {
  timeout = 5s
  send_batch_size = 1024
  send_batch_max_size = 2048
  
  output {
    metrics = [otelcol.exporter.prometheus.default.input]
    logs    = [otelcol.exporter.loki.default.input]
    traces  = [otelcol.exporter.otlp.tempo.input]
  }
}

// Resource Processor (add labels)
otelcol.processor.resource "default" {
  attributes {
    key = "environment"
    value = "production"
    action = "insert"
  }
  
  attributes {
    key = "cluster"
    value = "homelab"
    action = "insert"
  }
}

// Prometheus Exporter
otelcol.exporter.prometheus "default" {
  forward_to = [prometheus.remote_write.local.receiver]
}

prometheus.remote_write "local" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}

// Loki Exporter
otelcol.exporter.loki "default" {
  forward_to = [loki.write.local.receiver]
}

loki.write "local" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}

// Tempo Exporter
otelcol.exporter.otlp "tempo" {
  client {
    endpoint = "tempo:4317"
    tls {
      insecure = true  // Internal Docker network
    }
  }
}

// Prometheus Scraping (local exporters)
prometheus.scrape "node_exporter" {
  targets = [
    {"__address__" = "bastion.lab:9100", "job" = "node", "instance" = "bastion"},
    {"__address__" = "monster.lab:9100", "job" = "node", "instance" = "monster"},
  ]
  
  forward_to = [prometheus.remote_write.local.receiver]
  
  scrape_interval = "15s"
  scheme = "https"
  
  tls_config {
    cert_file = "/etc/certs/alloy-client.crt"
    key_file  = "/etc/certs/alloy-client.key"
    ca_file   = "/etc/certs/ca.crt"
  }
}

// Journald Log Collection
loki.source.journal "system_logs" {
  path = "/var/log/journal"
  labels = {
    job = "systemd",
    host = env("HOSTNAME"),
  }
  
  forward_to = [loki.write.local.receiver]
}

// Docker Log Collection
loki.source.docker "container_logs" {
  host = "unix:///var/run/docker.sock"
  labels = {
    job = "docker",
    host = env("HOSTNAME"),
  }
  
  forward_to = [loki.write.local.receiver]
}
```

### 3. Loki Configuration

```yaml
# loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096
  log_level: info

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

storage_config:
  tsdb_shipper:
    active_index_directory: /loki/tsdb-index
    cache_location: /loki/tsdb-cache
    shared_store: filesystem
  
  filesystem:
    directory: /loki/chunks

limits_config:
  retention_period: 720h  # 30 days
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20
  max_query_series: 10000
  max_query_lookback: 720h
  reject_old_samples: true
  reject_old_samples_max_age: 168h  # 1 week

compactor:
  working_directory: /loki/compactor
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  retention_delete_worker_count: 150

querier:
  max_concurrent: 4

query_range:
  align_queries_with_step: true
  cache_results: true
  
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100
```

### 4. Tempo Configuration

```yaml
# tempo.yml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        http:
          endpoint: 0.0.0.0:4318
        grpc:
          endpoint: 0.0.0.0:4317

ingester:
  trace_idle_period: 10s
  max_block_bytes: 1_000_000
  max_block_duration: 5m

compactor:
  compaction:
    compacted_block_retention: 1h
    block_retention: 168h  # 7 days
    compaction_window: 1h
    max_compaction_objects: 1000000

storage:
  trace:
    backend: local
    wal:
      path: /var/tempo/wal
    local:
      path: /var/tempo/traces
    pool:
      max_workers: 100
      queue_depth: 10000

querier:
  max_concurrent_queries: 20
  frontend_worker:
    frontend_address: localhost:9095

query_frontend:
  search:
    max_duration: 0  # No limit
```

---

## 📝 Ansible Role Structure

```
roles/monitoring/
├── defaults/
│   └── main.yml              # Default variables
├── tasks/
│   ├── main.yml              # Entry point
│   ├── certificates.yml      # Generate monitoring certs
│   ├── prometheus.yml        # Deploy Prometheus
│   ├── grafana.yml           # Deploy Grafana
│   ├── loki.yml              # Deploy Loki
│   ├── tempo.yml             # Deploy Tempo
│   ├── alloy.yml             # Deploy Grafana Alloy
│   ├── alertmanager.yml      # Deploy AlertManager
│   ├── exporters.yml         # Deploy node_exporter, cAdvisor
│   ├── firewall.yml          # Configure firewall rules
│   └── dashboards.yml        # Import Grafana dashboards
├── templates/
│   ├── monitoring.compose.j2         # Docker Compose
│   ├── prometheus.yml.j2             # Prometheus config
│   ├── alloy-config.alloy.j2         # Alloy config
│   ├── loki-config.yml.j2            # Loki config
│   ├── tempo.yml.j2                  # Tempo config
│   ├── grafana.ini.j2                # Grafana config
│   ├── alertmanager.yml.j2           # AlertManager config
│   ├── alert-rules.yml.j2            # Prometheus alert rules
│   ├── node-exporter-web-config.yml.j2  # Exporter mTLS
│   └── dashboards/
│       ├── infrastructure.json.j2
│       ├── gpu-monitoring.json.j2
│       ├── container-health.json.j2
│       ├── service-performance.json.j2
│       └── security.json.j2
├── files/
│   └── dashboards/           # Static dashboard JSONs
├── handlers/
│   └── main.yml              # Service restart handlers
└── vars/
    └── main.yml              # Role variables
```

---

## ✅ Acceptance Criteria

### Phase 1 Complete When:
- [ ] Grafana accessible at https://grafana.lab with mTLS
- [ ] Prometheus scraping metrics from Bastion
- [ ] Dashboard showing CPU, RAM, Disk, Network in real-time
- [ ] Alert fires when disk usage > 90%
- [ ] All connections use mTLS certificates
- [ ] Metrics retained for 30 days

### Phase 2 Complete When:
- [ ] Container metrics visible in Grafana
- [ ] GPU temperature and utilization tracked (Monster)
- [ ] Traefik request rate graphed
- [ ] Alert fires on container restart
- [ ] Alert fires on GPU temp > 85°C
- [ ] Can identify highest CPU container

### Phase 3 Complete When:
- [ ] All system logs searchable in Grafana
- [ ] Security dashboard shows SSH failures
- [ ] Firewall block events tracked
- [ ] Alert fires on SSH brute force (>5 failures/min)
- [ ] Logs correlated with metrics
- [ ] 30-day log retention working

### Phase 4 Complete When:
- [ ] Grafana Alloy receiving OTLP data
- [ ] Remote hosts sending metrics via OTEL
- [ ] mTLS enforced on all OTLP connections
- [ ] Pipeline latency < 10 seconds
- [ ] Documentation for adding new services
- [ ] No data loss during network issues

### Phase 5 Complete When:
- [ ] Tempo storing traces
- [ ] Sample app instrumented with OTEL SDK
- [ ] Full request trace visible (Traefik → App → DB)
- [ ] Latency breakdown by service shown
- [ ] Trace correlation with logs/metrics working
- [ ] 30-day trace retention (with sampling)

### Phase 6 Complete When:
- [ ] AlertManager delivering notifications
- [ ] Slack/Discord integration working
- [ ] Critical alerts routed correctly
- [ ] Runbooks linked from alerts
- [ ] Alert silencing functional
- [ ] < 1 minute notification latency

---

## 🎓 Learning Resources

### Official Documentation
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/grafana/latest/)
- [Loki](https://grafana.com/docs/loki/latest/)
- [Tempo](https://grafana.com/docs/tempo/latest/)
- [Grafana Alloy](https://grafana.com/docs/alloy/latest/)
- [OpenTelemetry](https://opentelemetry.io/docs/)

### Community Dashboards
- [Grafana Dashboard Library](https://grafana.com/grafana/dashboards/)
- [Node Exporter Full (ID: 1860)](https://grafana.com/grafana/dashboards/1860)
- [Docker Container Metrics (ID: 193)](https://grafana.com/grafana/dashboards/193)
- [NVIDIA GPU Metrics (ID: 12375)](https://grafana.com/grafana/dashboards/12375)

### Best Practices
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

---

## 🔄 Related Technical Debt

- [Full mTLS Implementation](./full-mtls.md) - Dependencies on monitoring for cert expiry alerts
- Kubernetes Migration - Tempo and service mesh integration depends on K8s
- Backup Strategy - Monitoring data retention and backup automation
- Security Hardening - SIEM integration with log aggregation

---

## 📅 Timeline

| Phase | Duration | Start Date | End Date | Status |
|-------|----------|------------|----------|--------|
| Phase 1: Foundation | 1 week | TBD | TBD | 🔴 Not Started |
| Phase 2: Container Metrics | 1 week | TBD | TBD | 🔴 Not Started |
| Phase 3: Log Aggregation | 1 week | TBD | TBD | 🔴 Not Started |
| Phase 4: Unified Pipeline | 1 week | TBD | TBD | 🔴 Not Started |
| Phase 5: Tracing | 1 week | Post-K8s | Post-K8s | 🔴 Blocked by K8s |
| Phase 6: Alerting | Ongoing | TBD | TBD | 🔴 Not Started |

**Total Estimated Effort**: 4-5 weeks (excluding Phase 5 which waits for K8s)

---

## 🎯 Success Metrics

After full implementation, we should achieve:

- ✅ **100% infrastructure visibility** - All hosts, containers, services monitored
- ✅ **< 5 minute MTTR** - Mean time to resolution with logs + metrics + traces
- ✅ **99.9% uptime tracking** - SLA monitoring for critical services
- ✅ **Proactive alerting** - Issues detected before user impact
- ✅ **Security compliance** - All monitoring endpoints mTLS protected
- ✅ **30-day retention** - Historical data for troubleshooting and forensics
- ✅ **< 1% overhead** - Monitoring uses minimal resources
- ✅ **Zero data loss** - Buffering and reliability during outages

---

## 📌 Notes

- This observability stack is designed to scale from current Docker setup to future Kubernetes deployment
- mTLS integration is first-class, not bolted on later
- Storage requirements assume 30-day retention; adjust based on available disk
- Grafana Alloy chosen over older Grafana Agent for better OTEL support
- Tempo trace retention can be reduced to 7 days with sampling to save storage
- Alert fatigue prevention is critical - tune alert thresholds carefully
- All exporters should run as non-root where possible (security)
- Consider log sampling for high-volume containers to reduce storage

---

**Last Updated**: 2024-02-01  
**Owner**: Infrastructure Team  
**Reviewers**: Security Team (mTLS review), Platform Team (K8s integration)  
**Status**: 🔴 Planning - Not Started
