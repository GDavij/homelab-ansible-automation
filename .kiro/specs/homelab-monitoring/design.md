# Design Document

## Overview

This design document outlines the integration of Prometheus metrics collection and Grafana visualization into the existing homelab infrastructure automation system. The monitoring stack will provide **comprehensive deep observability** for Traefik reverse proxy and AdGuard Home DNS service, with **extreme binding** between these services and the monitoring system to enable advanced network topology visualization, zone-based traffic analysis, and complete network graph generation.

The solution leverages local storage on the bastion host at `/opt/core/` for core monitoring services, integrates with the existing PKI infrastructure using certificates from the established PKI role patterns, and provides **advanced network topology visualization capabilities** including:
- **Complete network graph generation** showing all nodes, connections, and traffic flows
- **Zone-based traffic analysis** with detailed client-to-service mapping
- **Real-time network topology updates** reflecting current traffic patterns
- **Domain-to-IP mapping visualization** with access frequency analysis
- **Load distribution tracking** across all services and network paths

The monitoring services will be deployed as Docker containers alongside existing infrastructure services, following the established patterns in `roles/infra_gateways`, with **mandatory mTLS communication** for all inter-container connections.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Bastion Host (192.168.1.77)"
        subgraph "Existing Services"
            T[Traefik<br/>Gateway]
            A[AdGuard<br/>DNS]
            ES[Existing Services<br/>Memos, Maybe, etc.]
        end
        
        subgraph "Monitoring Stack"
            P[Prometheus<br/>512MB]
            G[Grafana<br/>384MB]
            NE[Node Exporter<br/>64MB]
            AE[AdGuard Exporter<br/>40MB]
        end
        
        subgraph "Storage"
            PS[/opt/core/prometheus/]
            GS[/opt/core/grafana/]
        end
        
        subgraph "PKI Certificates"
            PKI[/etc/pki/homelab/]
        end
    end
    
    subgraph "Network Zones (Firewalld)"
        UZ[underlay_network<br/>192.168.1.0/24]
        EZ[external<br/>Internet]
        TZ[trusted<br/>localhost]
    end
    
    subgraph "Clients"
        C1[Client 1]
        C2[Client 2]
        CN[Client N]
    end
    
    %% Data Flow
    C1 --> T
    C2 --> T
    CN --> T
    
    T --> ES
    T --> G
    
    C1 --> A
    C2 --> A
    CN --> A
    
    %% Monitoring Flow
    P -.->|scrape| T
    P -.->|scrape| A
    P -.->|scrape| NE
    P -.->|scrape| AE
    
    AE -.->|parse logs| A
    G -.->|query| P
    
    %% Storage
    P --> PS
    G --> GS
    
    %% PKI
    PKI -.->|certs| T
    PKI -.->|certs| A
    PKI -.->|certs| P
    PKI -.->|certs| G
    PKI -.->|certs| AE
    PKI -.->|certs| NE
    
    %% Network Zones
    C1 -.-> UZ
    C2 -.-> UZ
    CN -.-> UZ
    
    classDef monitoring fill:#e1f5fe
    classDef existing fill:#f3e5f5
    classDef storage fill:#fff3e0
    classDef network fill:#e8f5e8
    
    class P,G,NE,AE monitoring
    class T,A,ES existing
    class PS,GS,PKI storage
    class UZ,EZ,TZ network
```

### mTLS Communication Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant T as Traefik
    participant P as Prometheus
    participant G as Grafana
    participant AE as AdGuard Exporter
    participant A as AdGuard Home
    
    Note over C,A: All communications use mTLS with homelab CA
    
    C->>+T: HTTPS Request (client cert)
    T->>T: Validate client cert
    T->>-C: Response (server cert)
    
    P->>+T: Scrape metrics (prometheus cert)
    T->>T: Validate server cert
    T->>-P: Metrics data (traefik cert)
    
    P->>+AE: Scrape DNS metrics (prometheus cert)
    AE->>AE: Validate server cert
    AE->>-P: DNS metrics (adguard-exporter cert)
    
    AE->>+A: Query AdGuard API (adguard-exporter cert)
    A->>A: Validate server cert
    A->>-AE: DNS logs/stats (adguard cert)
    
    G->>+P: Query metrics (grafana cert)
    P->>P: Validate server cert
    P->>-G: Time series data (prometheus cert)
    
    C->>+G: Dashboard access (client cert)
    G->>G: Validate client cert
    G->>-C: Dashboard (grafana cert)
    
    C->>+P: External analytics access (client cert)
    P->>P: Validate client cert
    P->>-C: Metrics data (prometheus cert)
```

### Network Topology Data Flow

```mermaid
flowchart TD
    subgraph "Data Sources"
        CR[Client Requests]
        DQ[DNS Queries]
        SL[Service Logs]
    end
    
    subgraph "Collection Layer"
        T[Traefik<br/>Deep Labels]
        AE[AdGuard Exporter<br/>Log Parser]
        NE[Node Exporter<br/>System Metrics]
    end
    
    subgraph "Processing Layer"
        P[Prometheus<br/>Time Series DB]
    end
    
    subgraph "Visualization Layer"
        G[Grafana<br/>Network Graph]
        NT[Network Topology<br/>Dashboard]
        ZA[Zone Analysis<br/>Dashboard]
    end
    
    subgraph "Network Graph Elements"
        SN[Service Nodes]
        CN[Client Nodes]
        EN[External Nodes]
        TE[Traffic Edges]
        ZB[Zone Boundaries]
    end
    
    %% Data Flow
    CR --> T
    DQ --> AE
    SL --> AE
    
    T --> P
    AE --> P
    NE --> P
    
    P --> G
    P --> NT
    P --> ZA
    
    G --> SN
    G --> CN
    G --> EN
    G --> TE
    G --> ZB
    
    %% Annotations
    T -.->|"Request metadata<br/>Client zones<br/>Service mapping"| P
    AE -.->|"DNS resolution<br/>Domain-IP mapping<br/>Client behavior"| P
    NE -.->|"System resources<br/>Container health"| P
    
    classDef source fill:#ffecb3
    classDef collection fill:#e1f5fe
    classDef processing fill:#f3e5f5
    classDef visualization fill:#e8f5e8
    classDef graph fill:#fff3e0
    
    class CR,DQ,SL source
    class T,AE,NE collection
    class P processing
    class G,NT,ZA visualization
    class SN,CN,EN,TE,ZB graph
```

### PKI Certificate Relationships

```mermaid
graph TB
    subgraph "PKI Infrastructure"
        RCA[Root CA<br/>lab]
        
        subgraph "Service Certificates"
            TC[traefik.crt<br/>gateway.lab]
            AC[adguard.crt<br/>dns.lab]
            PC[prometheus.crt<br/>prometheus.lab]
            GC[grafana.crt<br/>grafana.lab]
            AEC[adguard-exporter.crt<br/>adguard-exporter.lab]
            NEC[node-exporter.crt<br/>node-exporter.lab]
        end
    end
    
    subgraph "Certificate Usage"
        subgraph "Server Authentication"
            TS[Traefik Server]
            AS[AdGuard Server]
            PS[Prometheus Server]
            GS[Grafana Server]
            AES[AdGuard Exporter]
            NES[Node Exporter]
        end
        
        subgraph "Service-to-Service Communication"
            PSC[Prometheus → Targets]
            GSC[Grafana → Prometheus]
            AESC[AdGuard Exporter → AdGuard]
        end
        
        subgraph "External Access"
            EA[External Analytics<br/>→ Prometheus]
        end
    end
    
    %% Certificate Issuance
    RCA --> TC
    RCA --> AC
    RCA --> PC
    RCA --> GC
    RCA --> AEC
    RCA --> NEC
    
    %% Certificate Usage
    TC --> TS
    AC --> AS
    PC --> PS
    GC --> GS
    AEC --> AES
    NEC --> NES
    
    PC --> PSC
    GC --> GSC
    AEC --> AESC
    
    %% mTLS Connections (Service-to-Service)
    PSC -.->|mTLS| TS
    PSC -.->|mTLS| AES
    PSC -.->|mTLS| NES
    GSC -.->|mTLS| PS
    AESC -.->|mTLS| AS
    
    %% External Access via Traefik
    EA -.->|HTTPS via Traefik| PS
    
    classDef ca fill:#ffcdd2
    classDef server fill:#e8f5e8
    classDef usage fill:#fff3e0
    classDef external fill:#e1f5fe
    
    class RCA ca
    class TC,AC,PC,GC,AEC,NEC server
    class TS,AS,PS,GS,AES,NES,PSC,GSC,AESC usage
    class EA external
```

## Components and Interfaces

### Core Components

#### 1. Prometheus (Metrics Collection Engine)
- **Resource Allocation**: 512MB RAM maximum
- **Storage**: Local TSDB with 30-day retention
- **Scrape Interval**: 30 seconds (optimized for low CPU usage)
- **Configuration**: YAML-based with service discovery via Docker labels

#### 2. Grafana (Visualization Platform)
- **Resource Allocation**: 384MB RAM maximum
- **Features**: Dashboards, alerting, node graph visualization
- **Disabled Features**: Image rendering, complex plugins
- **Authentication**: Integration with existing homelab users

#### 3. Node Exporter (System Metrics)
- **Resource Allocation**: 64MB RAM maximum
- **Collectors**: Minimal set (CPU, memory, disk, network)
- **Configuration**: Optimized collector selection for hardware constraints

#### 4. AdGuard Exporter (Custom Component)
- **Resource Allocation**: 40MB RAM maximum
- **Function**: Deep integration with AdGuard Home for comprehensive DNS monitoring
- **Advanced Metrics**: 
  - DNS queries with client zone mapping
  - Blocked domains with threat intelligence
  - Client activity patterns and geographic grouping
  - Domain-to-IP resolution tracking
  - Upstream server performance analysis
- **Network Graph Data**: Provides client-to-domain relationship data for network topology visualization
- **Zone Analysis**: Categorizes traffic by network zones for security and performance analysis

### Interface Specifications

#### Deep Traefik Metrics Integration
The monitoring stack requires **extreme binding** with Traefik to capture comprehensive network topology data:

```yaml
# Enhanced Traefik configuration for deep observability
api:
  dashboard: true
  debug: true
  insecure: false

metrics:
  prometheus:
    addEntryPointsLabels: true
    addServicesLabels: true
    addRoutersLabels: true
    buckets:
      - 0.1
      - 0.3
      - 1.2
      - 5.0
    entryPoint: metrics

# Additional labels for network topology
labels:
  - "monitoring.zone={{ client_zone }}"
  - "monitoring.service_type={{ service_type }}"
  - "monitoring.backend_health={{ backend_health }}"
  - "monitoring.client_network={{ client_network }}"
```

#### Enhanced Prometheus Configuration Interface
```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s
  external_labels:
    cluster: 'homelab'
    environment: 'production'

# TLS server configuration for Prometheus web interface
tls_server_config:
  cert_file: /etc/prometheus/certs/prometheus.crt
  key_file: /etc/prometheus/certs/prometheus.key
  client_ca_file: /etc/prometheus/certs/root-ca.crt
  client_auth_type: RequireAndVerifyClientCert

scrape_configs:
  - job_name: 'traefik'
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/certs/root-ca.crt
      cert_file: /etc/prometheus/certs/prometheus.crt
      key_file: /etc/prometheus/certs/prometheus.key
      server_name: gateway.lab
      insecure_skip_verify: false
    static_configs:
      - targets: ['gateway:8080']
    metrics_path: '/metrics'
    scrape_interval: 15s
    
  - job_name: 'adguard-exporter'
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/certs/root-ca.crt
      cert_file: /etc/prometheus/certs/prometheus.crt
      key_file: /etc/prometheus/certs/prometheus.key
      server_name: adguard-exporter.lab
    static_configs:
      - targets: ['adguard-exporter:9617']
    scrape_interval: 15s
    
  - job_name: 'node-exporter'
    scheme: https
    tls_config:
      ca_file: /etc/prometheus/certs/root-ca.crt
      cert_file: /etc/prometheus/certs/prometheus.crt
      key_file: /etc/prometheus/certs/prometheus.key
      server_name: node-exporter.lab
    static_configs:
      - targets: ['node-exporter:9100']
    params:
      collect[]:
        - cpu
        - meminfo
        - diskstats
        - netdev
        - filesystem
```

#### Docker Service Discovery Interface
```yaml
# Monitoring service labels following existing patterns
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.prometheus.rule=Host(`prometheus.lab`)"
  - "traefik.http.routers.prometheus.entrypoints=websecure"
  - "traefik.http.routers.prometheus.tls=true"
  - "traefik.http.services.prometheus.loadbalancer.server.port=9090"
  - "traefik.http.services.prometheus.loadbalancer.server.scheme=https"
  - "traefik.http.services.prometheus.loadbalancer.serverstransport=prometheus-transport@file"
```

#### Enhanced AdGuard Exporter Configuration Interface
```yaml
# AdGuard Home API configuration with deep integration
adguard:
  url: "https://dns:443"
  username: "admin"
  password_file: "/run/secrets/adguard_password"
  tls_config:
    ca_file: "/etc/adguard-exporter/certs/root-ca.crt"
    cert_file: "/etc/adguard-exporter/certs/adguard-exporter.crt"
    key_file: "/etc/adguard-exporter/certs/adguard-exporter.key"
    server_name: "dns.lab"
  
# Enhanced metrics configuration for network topology
metrics:
  listen_address: ":9617"
  log_level: "info"
  scrape_interval: "15s"  # Increased frequency for real-time topology
  tls_config:
    cert_file: "/etc/adguard-exporter/certs/adguard-exporter.crt"
    key_file: "/etc/adguard-exporter/certs/adguard-exporter.key"
    ca_file: "/etc/adguard-exporter/certs/root-ca.crt"
  
# Deep log parsing for network graph generation
log_parsing:
  query_log_path: "/opt/adguardhome/data/querylog.json"
  stats_path: "/opt/adguardhome/data/stats.db"
  blocked_services_path: "/opt/adguardhome/data/blocked_services.json"
  enable_client_tracking: true
  enable_domain_mapping: true
  enable_zone_analysis: true
  
# Network zone configuration (using existing firewalld zones)
network_zones:
  - name: "underlay_network"
    cidr: "192.168.1.0/24"
    description: "Main homelab network zone (firewalld underlay_network)"
    firewalld_zone: "underlay_network"
    interfaces: ["{{ ansible_default_ipv4.interface }}"]
    services: ["ssh", "http", "https", "dns"]
    masquerading: true
  - name: "trusted"
    cidr: "127.0.0.0/8"
    description: "Trusted interfaces and localhost (firewalld trusted)"
    firewalld_zone: "trusted"
    interfaces: ["docker0", "tailscale0"]
    services: ["all"]
    masquerading: false
  - name: "external"
    cidr: "0.0.0.0/0"
    description: "External internet traffic (firewalld external)"
    firewalld_zone: "external"
    interfaces: []
    services: []
    masquerading: false
    
# Client classification for network graph
client_classification:
  enable_geographic_grouping: true
  enable_device_type_detection: true
  enable_behavior_analysis: true
```

#### Enhanced Grafana Data Source Interface
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: https://prometheus:9090
    access: proxy
    isDefault: true
    jsonData:
      tlsAuth: true
      tlsAuthWithCACert: true
      serverName: prometheus.lab
      httpMethod: POST
    secureJsonData:
      tlsCACert: |
        -----BEGIN CERTIFICATE-----
        # Root CA Certificate Content from /etc/pki/homelab/certs/root-ca.crt
        -----END CERTIFICATE-----
      tlsClientCert: |
        -----BEGIN CERTIFICATE-----
        # Grafana Service Certificate Content from /etc/pki/homelab/certs/grafana.crt
        -----END CERTIFICATE-----
      tlsClientKey: |
        -----BEGIN PRIVATE KEY-----
        # Grafana Service Private Key Content from /etc/pki/homelab/private/grafana.key
        -----END PRIVATE KEY-----
```

#### Grafana TLS Server Configuration
```ini
[server]
protocol = https
cert_file = /etc/grafana/certs/grafana.crt
cert_key = /etc/grafana/certs/grafana.key
root_url = https://grafana.lab/

[security]
# Enable client certificate authentication
client_cert_auth = true
ca_cert = /etc/grafana/certs/root-ca.crt
```

### Expected Network Graph Visualization

```mermaid
graph TB
    subgraph EZ["External Zone (firewalld: external)"]
        EXT[Internet<br/>External Services]
        DNS1[1.1.1.1<br/>Cloudflare DNS]
        DNS2[8.8.8.8<br/>Google DNS]
    end
    
    subgraph UZ["Underlay Network Zone (firewalld: underlay_network)<br/>192.168.1.0/24<br/>Physical Interface + Masquerading"]
        subgraph "Infrastructure Services (192.168.1.77)"
            T[Traefik<br/>gateway.lab<br/>🟢 Healthy]
            A[AdGuard<br/>dns.lab<br/>🟢 Healthy]
            P[Prometheus<br/>prometheus.lab<br/>🟢 Healthy]
            G[Grafana<br/>grafana.lab<br/>🟢 Healthy]
        end
        
        subgraph "Application Services (192.168.1.77)"
            M[Memos<br/>daily.lab<br/>🟢 Healthy]
            MF[Maybe Finance<br/>finance.lab<br/>🟢 Healthy]
            E[Excalidraw<br/>draw.lab<br/>🟢 Healthy]
            U[UpSnap<br/>snap.lab<br/>🟢 Healthy]
        end
        
        subgraph "Network Clients"
            C1[Client 1<br/>192.168.1.100<br/>Desktop]
            C2[Client 2<br/>192.168.1.101<br/>Mobile]
            C3[Client 3<br/>192.168.1.102<br/>Laptop]
        end
    end
    
    subgraph TZ["Trusted Zone (firewalld: trusted)<br/>docker0 + tailscale0 + localhost"]
        subgraph "Docker Network"
            DC[Docker Containers<br/>Core Services]
            NE[Node Exporter<br/>node-exporter.lab<br/>🟢 Healthy]
            AE[AdGuard Exporter<br/>adguard-exporter.lab<br/>🟢 Healthy]
        end
        
        subgraph "Tailscale Network"
            TS[Tailscale Interface<br/>tailscale0<br/>VPN Mesh]
        end
        
        subgraph "Localhost"
            L[System Services<br/>127.0.0.1<br/>Local Processes]
        end
    end
    
    %% Client to Services Traffic (HTTPS through Traefik)
    C1 -->|HTTPS<br/>SSH, HTTP, HTTPS<br/>ICMP allowed| T
    C2 -->|HTTPS<br/>5.2MB/s| T
    C3 -->|HTTPS<br/>3.1MB/s| T
    
    %% DNS Queries (Direct to AdGuard)
    C1 -->|DNS<br/>45 q/min<br/>Port 53 allowed| A
    C2 -->|DNS<br/>23 q/min| A
    C3 -->|DNS<br/>67 q/min| A
    
    %% Traefik Load Balancing to Backend Services
    T -->|Proxy<br/>2.1MB/s| M
    T -->|Proxy<br/>1.5MB/s| MF
    T -->|Proxy<br/>0.8MB/s| E
    T -->|Proxy<br/>0.3MB/s| U
    T -->|Proxy<br/>0.1MB/s| G
    T -->|Proxy<br/>0.05MB/s| P
    
    %% DNS Upstream Resolution (NAT Gateway)
    A -->|Upstream<br/>via Masquerading<br/>12ms avg| DNS1
    A -->|Upstream<br/>via Masquerading<br/>15ms avg| DNS2
    A -->|Upstream<br/>via Masquerading<br/>8ms avg| EXT
    
    %% Monitoring Data Collection (mTLS via Docker Network)
    P -.->|Scrape mTLS<br/>15s interval<br/>via docker0| T
    P -.->|Scrape mTLS<br/>15s interval<br/>via docker0| AE
    P -.->|Scrape mTLS<br/>30s interval<br/>via docker0| NE
    AE -.->|Parse Logs<br/>Real-time<br/>via docker0| A
    G -.->|Query mTLS<br/>Real-time<br/>via docker0| P
    
    %% Tailscale VPN Access
    TS -.->|VPN Mesh<br/>Secure Remote Access| UZ
    
    %% Zone Boundaries and Firewall Rules
    UZ -.->|Masquerading<br/>NAT Gateway| EZ
    UZ -.->|Trusted Interfaces<br/>docker0, tailscale0| TZ
    
    classDef external fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px
    classDef underlay fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef trusted fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef infrastructure fill:#e1f5fe,stroke:#1976d2,stroke-width:2px
    classDef application fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef client fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef monitoring fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef docker fill:#e3f2fd,stroke:#0277bd,stroke-width:2px
    classDef tailscale fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    
    class EXT,DNS1,DNS2 external
    class T,A infrastructure
    class M,MF,E,U application
    class C1,C2,C3 client
    class L localhost
    class P,G monitoring
    class DC,NE,AE docker
    class TS tailscale
```

### Comprehensive Metrics Data Model

#### Enhanced Traefik Metrics Schema
```
# Core request metrics with enhanced labeling for network topology
traefik_requests_total{service, method, code, backend, client_zone, client_ip}
traefik_request_duration_seconds{service, method, code, backend, client_zone}
traefik_backend_requests_total{backend, method, code, health_status}
traefik_backend_request_duration_seconds{backend, method, code}
traefik_tls_certs_not_after{cn, serial, issuer}

# Network topology specific metrics
traefik_service_connections_active{service, backend, client_zone}
traefik_client_service_mapping{client_ip, service, backend, zone}
traefik_load_balancer_distribution{backend, server, weight}
traefik_network_flow_bytes{source_zone, destination_service, direction}
traefik_route_health_status{route, backend, status}
```

#### Enhanced AdGuard Metrics Schema
```
# Core DNS metrics with network topology data
adguard_dns_queries_total{client_ip, client_zone, query_type, blocked, domain}
adguard_dns_query_duration_seconds{client_ip, client_zone, upstream, domain}
adguard_blocked_domains_total{domain, client_ip, client_zone, reason, threat_type}
adguard_upstream_response_time{upstream, status, client_zone}
adguard_client_requests_total{client_ip, network_zone, device_type}

# Network graph specific metrics
adguard_domain_ip_mapping{domain, resolved_ip, ttl, first_seen, last_seen}
adguard_client_domain_frequency{client_ip, domain, access_count, zone}
adguard_network_zone_traffic{source_zone, query_type, blocked_ratio}
adguard_client_behavior_score{client_ip, behavior_type, score, zone}
adguard_domain_category_mapping{domain, category, threat_level}
```

#### System Metrics Schema
```
node_cpu_seconds_total{cpu, mode}
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes
node_filesystem_size_bytes{device, fstype, mountpoint}
node_network_receive_bytes_total{device}
node_network_transmit_bytes_total{device}
```

### Network Graph Data Model

#### Node Definition for Network Topology
```json
{
  "id": "service_name",
  "title": "Service Display Name",
  "subtitle": "Service Type (DNS/Proxy/Client)",
  "mainstat": "Request Rate (req/s)",
  "secondarystat": "Error Rate (%)",
  "color": "status_color",
  "icon": "service_icon",
  "highlighted": false,
  "zone": "network_zone",
  "node_type": "service|client|external",
  "health_status": "healthy|degraded|unhealthy",
  "metadata": {
    "ip_address": "192.168.1.x",
    "last_seen": "timestamp",
    "device_type": "server|client|iot",
    "geographic_location": "zone_name"
  }
}
```

#### Edge Definition for Traffic Flows
```json
{
  "id": "connection_id",
  "source": "source_service",
  "target": "target_service",
  "mainstat": "Traffic Volume (MB/s)",
  "secondarystat": "Latency (ms)",
  "thickness": "traffic_weight",
  "highlighted": false,
  "color": "health_color",
  "connection_type": "http|dns|internal",
  "protocol": "tcp|udp|https",
  "metadata": {
    "bandwidth_utilization": "percentage",
    "packet_loss": "percentage",
    "connection_count": "active_connections",
    "last_activity": "timestamp"
  }
}
```

#### Zone Traffic Data Model for Network Segmentation
```
# Network zone traffic metrics
zone_traffic_bytes_total{source_zone, destination_zone, protocol, service}
zone_connections_total{source_zone, destination_zone, state, service_type}
zone_bandwidth_utilization{zone, direction, time_window}
client_zone_mapping{client_ip, zone_name, zone_type, device_category}

# Client-service relationship metrics
client_service_connections{client_ip, service_name, connection_type, zone}
service_dependency_graph{source_service, target_service, dependency_type}
network_path_latency{source_zone, destination_zone, path_type, latency_ms}
```

#### Domain Access Pattern Schema for Security Analysis
```
# Domain access and security metrics
domain_access_total{domain, client_ip, client_zone, access_type, blocked}
domain_ip_mapping{domain, resolved_ip, ttl, resolution_source}
client_domain_frequency{client_ip, domain, access_count, time_window}
suspicious_pattern_score{client_ip, domain, pattern_type, score, severity}
threat_intelligence_mapping{domain, threat_category, confidence_score}

# Network behavior analysis
client_behavior_profile{client_ip, behavior_type, frequency, anomaly_score}
network_anomaly_detection{source, destination, anomaly_type, severity}
traffic_baseline_deviation{metric_name, current_value, baseline_value, deviation_percentage}
```

## Required Grafana Dashboards

### Network Topology Dashboard
**Primary Dashboard**: Complete network graph visualization showing all nodes and connections

#### Features Required:
- **Real-time Network Graph**: Interactive node graph showing all services, clients, and external connections
- **Zone-based Visualization**: Color-coded zones (internal, IoT, guest, external) with clear boundaries
- **Traffic Flow Animation**: Animated edges showing real-time traffic flow direction and volume
- **Node Details**: Click-through to detailed metrics for each node (service/client)
- **Health Status Indicators**: Visual health status for all nodes and connections
- **Load Distribution**: Visual representation of load balancing across backend services

#### Graph Elements:
- **Service Nodes**: Traefik, AdGuard, Prometheus, Grafana, and all monitored services
- **Client Nodes**: All active clients grouped by network zone
- **External Nodes**: External DNS servers, internet destinations
- **Connection Edges**: HTTP requests, DNS queries, internal service communication

### Zone Traffic Analysis Dashboard
**Secondary Dashboard**: Detailed zone-based traffic analysis

#### Features Required:
- **Zone Traffic Matrix**: Heat map showing traffic volume between all network zones
- **Client Activity by Zone**: Detailed breakdown of client activity within each zone
- **Bandwidth Utilization**: Real-time and historical bandwidth usage per zone
- **Top Talkers**: Most active clients and services by zone
- **Security Events**: Blocked requests and suspicious activity by zone

### Domain and DNS Analysis Dashboard
**Tertiary Dashboard**: Deep DNS and domain access analysis

#### Features Required:
- **Domain Access Frequency**: Most accessed domains with client mapping
- **DNS Query Analysis**: Query types, response times, and success rates
- **Blocked Domain Tracking**: Security blocks with threat intelligence
- **Client-Domain Relationships**: Graph showing which clients access which domains
- **Geographic Domain Mapping**: Domain resolution patterns by client location

### Service Performance Dashboard
**Quaternary Dashboard**: Individual service deep-dive metrics

#### Features Required:
- **Traefik Performance**: Request rates, response times, backend health per service
- **AdGuard Performance**: DNS resolution times, blocking effectiveness, upstream health
- **Load Balancing Analysis**: Backend distribution, health checks, failover events
- **Certificate Monitoring**: SSL certificate expiration tracking and renewal status

### Certificate Path Configuration

The monitoring stack integrates with the existing PKI infrastructure using the established certificate deployment patterns from the `roles/pki` role. Following the existing homelab pattern, certificates are deployed to `/etc/pki/homelab/` on the target hosts.

#### Certificate Deployment Strategy
The monitoring services will mount certificates from the deployed PKI location `/etc/pki/homelab/` into containers at runtime, following the same pattern as existing services like Traefik and AdGuard. **All inter-container communication will use HTTPS with mTLS authentication as a core requirement.** This approach ensures:

1. **Certificate Consistency**: Uses the same certificate generation and deployment patterns as other homelab services
2. **Automatic Renewal**: Leverages existing PKI automation for certificate lifecycle management through the `roles/pki` workflow
3. **Security Compliance**: Maintains the established security model with proper certificate validation using the homelab root CA
4. **mTLS Enforcement**: All monitoring service communications use mutual TLS authentication for maximum security
5. **Operational Simplicity**: Integrates seamlessly with existing Ansible automation workflows

#### Certificate Generation Integration
The monitoring stack will extend the existing `pki_services` variable in `group_vars/all.yml` to include all monitoring components:
```yaml
pki_services:
  # ... existing services (adguard, traefik, upsnap, excalidraw, memos, maybe_finance)
  - name: prometheus
    dns: prometheus.lab
    description: Prometheus Monitoring Service
    ip: 192.168.1.77
  - name: grafana
    dns: grafana.lab
    description: Grafana Visualization Service
    ip: 192.168.1.77
  - name: adguard-exporter
    dns: adguard-exporter.lab
    description: AdGuard Metrics Exporter Sidecar
    ip: 192.168.1.77
  - name: node-exporter
    dns: node-exporter.lab
    description: System Metrics Exporter
    ip: 192.168.1.77
```

This ensures the PKI role automatically generates server certificates for all monitoring services using the established patterns from `roles/pki/tasks/service-certs.yml`. All monitoring services will use their own service certificates for both server authentication and client authentication when communicating with other services.

## Error Handling

### Prometheus Error Handling
- **Scrape Target Failures**: Implement exponential backoff with maximum retry limits
- **Storage Failures**: Graceful degradation with alerting when disk space is insufficient
- **Memory Pressure**: Automatic reduction of retention period and scrape frequency
- **Configuration Errors**: Validation before applying configuration changes with rollback capability

### Grafana Error Handling
- **Dashboard Load Failures**: Fallback to basic system dashboards when custom dashboards fail
- **Data Source Connectivity**: Automatic retry with user notification of data source issues
- **Authentication Failures**: Clear error messages with guidance for certificate installation
- **Resource Exhaustion**: Automatic disabling of resource-intensive visualizations

### Network and Service Discovery Error Handling
- **DNS Resolution Failures**: Fallback to IP-based access with monitoring of DNS health
- **Certificate Validation Errors**: Detailed logging with certificate status reporting
- **Service Registration Failures**: Automatic retry with manual override capabilities
- **Traefik Integration Issues**: Health checks with automatic service deregistration for failed services

### Data Persistence Error Handling
- **Disk Space Exhaustion**: Automatic cleanup of old data with configurable emergency thresholds
- **File System Errors**: Graceful handling with data integrity verification
- **Backup Failures**: Alerting and retry mechanisms for critical data protection
- **Container Restart Data Loss**: Verification of mount points and data consistency checks

## Ansible Integration

### Role Structure
The monitoring stack will be implemented as an extension to the existing `roles/infra_gateways` role, following the established homelab patterns:

#### Template Integration
- **Docker Compose Extension**: Extend `roles/infra_gateways/templates/infra_services.compose.j2` to include Prometheus and Grafana services
- **Traefik Dynamic Configuration**: Add monitoring service routes to `roles/infra_gateways/templates/traefik-dynamic.yml.j2`
- **Configuration Templates**: Create dedicated templates for Prometheus and Grafana configurations

#### Variable Management
Following the existing pattern in `group_vars/Gateways/`:
- **Monitoring Configuration**: Add `group_vars/Gateways/monitoring.yml` for monitoring-specific variables
- **Service Integration**: Extend existing service configurations to include monitoring endpoints
- **Resource Constraints**: Define memory and CPU limits in group variables

#### Deployment Strategy
- **Incremental Deployment**: Add monitoring services to existing Docker Compose stack without disrupting current services
- **Configuration Management**: Use Ansible templates for all configuration files
- **Service Dependencies**: Ensure proper startup order and health checks
- **Rollback Capability**: Maintain ability to disable monitoring services if resource constraints are exceeded

### Infrastructure Patterns
The monitoring implementation will follow established homelab infrastructure patterns:

#### Service Discovery Pattern
```yaml
# Following existing ztn_labels macro pattern
{% macro monitoring_labels(name, dns, port=9090, scheme='https') -%}
- "traefik.enable=true"
- "traefik.http.routers.{{ name }}.rule=Host(`{{ dns }}`)"
- "traefik.http.routers.{{ name }}.entrypoints=websecure"
- "traefik.http.routers.{{ name }}.tls=true"
- "traefik.http.services.{{ name }}.loadbalancer.server.port={{ port }}"
- "traefik.http.services.{{ name }}.loadbalancer.server.scheme={{ scheme }}"
- "traefik.http.services.{{ name }}.loadbalancer.serverstransport={{ name }}-transport@file"
{%- endmacro %}
```

#### Network Integration
- **Core Network**: Connect monitoring services to existing `core_net` network with mTLS enforcement
- **Proxy Network**: Ensure Traefik can route to monitoring services via `proxy_net` using HTTPS only
- **Security Policies**: Apply same firewall and security policies as existing services, with additional mTLS validation
- **Certificate Validation**: All inter-service communication must validate certificates against the homelab root CA

#### Storage Management
- **Persistent Volumes**: Mount `/opt/core/prometheus/` and `/opt/core/grafana/` for data persistence
- **Backup Integration**: Include monitoring data in existing backup strategies
- **Retention Policies**: Implement automated cleanup to prevent disk exhaustion