# Requirements Document

## Introduction

Deploy a full observability stack split between the bastion host (Docker Compose via Ansible) and the Kubernetes cluster (GitOps manifests). The bastion hosts VictoriaMetrics (metrics storage), Grafana (dashboards), and Jaeger (tracing) — each with ghostunnel mTLS sidecars following existing patterns. The K8s OTEL Collector is updated to export to these real backends over mTLS, and a new MongoDB database is added to K8s (scaled to zero, ready when needed).

## Glossary

- **Bastion_Host**: The gateway machine running Docker Compose services managed by Ansible (`infra_gateways` and `apps_gateways` roles)
- **Ghostunnel_Sidecar**: A TLS-terminating proxy container that shares the network namespace with its parent service, listening on port 8443 and forwarding to the service's native port on 127.0.0.1
- **OTEL_Collector**: The OpenTelemetry Collector running in the K8s `observability` namespace, receiving telemetry via OTLP and exporting to backends
- **VictoriaMetrics**: A Prometheus-compatible time-series database for metrics storage, accessible at `metrics.lab`
- **Grafana**: A dashboarding and visualization platform, accessible at `dash.lab`, pre-configured with datasources
- **Jaeger**: A distributed tracing backend, accessible at `traces.lab`
- **MongoDB**: A document database deployed in the K8s `database` namespace, following the Qdrant manifest pattern
- **MongoDB_HPA**: A Kubernetes HorizontalPodAutoscaler that automatically scales MongoDB replicas based on CPU and memory utilization
- **PKI_Service**: An entry in the `pki_services` list in `group_vars/all.yml` that triggers certificate generation for a service
- **DNS_Rewrite**: An entry in `adguard_rewrites` that maps an FQDN to the gateway IP for split-horizon DNS resolution
- **HTTP_Router**: A Traefik dynamic configuration entry that routes incoming HTTPS requests to a backend service via its ghostunnel sidecar
- **Prometheus_Remote_Write**: A protocol for pushing metrics to a Prometheus-compatible backend (used by OTEL Collector to send metrics to VictoriaMetrics)
- **OTLP**: OpenTelemetry Protocol, used for transmitting traces from OTEL Collector to Jaeger

## Requirements

### Requirement 1: VictoriaMetrics Deployment on Bastion Host

**User Story:** As a platform operator, I want VictoriaMetrics deployed on the bastion host with mTLS, so that I have a Prometheus-compatible metrics backend reachable from the K8s cluster.

#### Acceptance Criteria

1. WHEN the Ansible playbook runs, THE Infra_Gateways_Role SHALL create the `/opt/core/victoriametrics` data directory on the Bastion_Host
2. WHEN the Docker Compose template is rendered, THE Compose_File SHALL contain a `victoriametrics` service using the image version from `versions.yml`
3. WHEN the Docker Compose template is rendered, THE Compose_File SHALL contain a `victoriametrics-sidecar` Ghostunnel_Sidecar that listens on port 8443 and forwards to the VictoriaMetrics native HTTP port on 127.0.0.1
4. WHEN the `victoriametrics-sidecar` starts, THE Ghostunnel_Sidecar SHALL mount the `victoriametrics` PKI certificate, key, and root CA from `/etc/pki/homelab/`
5. WHEN the `victoriametrics` service is deployed, THE Compose_File SHALL attach the service to the `core_net` Docker network
6. WHEN the `versions.yml` file is read, THE Versions_File SHALL contain a `victoriametrics_version` variable

### Requirement 2: Grafana Deployment on Bastion Host

**User Story:** As a platform operator, I want Grafana deployed on the bastion host with pre-configured datasources, so that I can visualize metrics and traces without manual setup.

#### Acceptance Criteria

1. WHEN the Ansible playbook runs, THE Infra_Gateways_Role SHALL create the `/opt/core/grafana` data directory on the Bastion_Host
2. WHEN the Docker Compose template is rendered, THE Compose_File SHALL contain a `grafana` service using the image version from `versions.yml`
3. WHEN the Docker Compose template is rendered, THE Compose_File SHALL contain a `grafana-sidecar` Ghostunnel_Sidecar that listens on port 8443 and forwards to the Grafana native HTTP port on 127.0.0.1
4. WHEN the `grafana-sidecar` starts, THE Ghostunnel_Sidecar SHALL mount the `grafana` PKI certificate, key, and root CA from `/etc/pki/homelab/`
5. WHEN the `grafana` service starts, THE Grafana_Instance SHALL load a provisioned datasources YAML file that configures VictoriaMetrics as a Prometheus-type datasource and Jaeger as a tracing datasource
6. WHEN the Ansible playbook runs, THE Infra_Gateways_Role SHALL render a `grafana_datasources.yml.j2` Jinja2 template and mount it into the Grafana container at the provisioning path
7. WHEN the `grafana` service is deployed, THE Compose_File SHALL attach the service to the `core_net` Docker network
8. WHEN the `versions.yml` file is read, THE Versions_File SHALL contain a `grafana_version` variable

### Requirement 3: Jaeger Deployment on Bastion Host

**User Story:** As a platform operator, I want Jaeger deployed on the bastion host with mTLS, so that I have a tracing backend reachable from the K8s cluster.

#### Acceptance Criteria

1. WHEN the Ansible playbook runs, THE Infra_Gateways_Role SHALL create the `/opt/core/jaeger` data directory on the Bastion_Host
2. WHEN the Docker Compose template is rendered, THE Compose_File SHALL contain a `jaeger` service using the image version from `versions.yml`
3. WHEN the Docker Compose template is rendered, THE Compose_File SHALL contain a `jaeger-sidecar` Ghostunnel_Sidecar that listens on port 8443 and forwards to the Jaeger native OTLP port on 127.0.0.1
4. WHEN the `jaeger-sidecar` starts, THE Ghostunnel_Sidecar SHALL mount the `jaeger` PKI certificate, key, and root CA from `/etc/pki/homelab/`
5. WHEN the `jaeger` service is deployed, THE Compose_File SHALL attach the service to the `core_net` Docker network
6. WHEN the `versions.yml` file is read, THE Versions_File SHALL contain a `jaeger_version` variable

### Requirement 4: PKI Certificate Generation

**User Story:** As a platform operator, I want TLS certificates generated for VictoriaMetrics, Grafana, and Jaeger, so that mTLS is enforced on all observability endpoints.

#### Acceptance Criteria

1. WHEN the `pki_services` list in `group_vars/all.yml` is read, THE PKI_Configuration SHALL contain an entry for `victoriametrics` with DNS `metrics.lab`
2. WHEN the `pki_services` list in `group_vars/all.yml` is read, THE PKI_Configuration SHALL contain an entry for `grafana` with DNS `dash.lab`
3. WHEN the `pki_services` list in `group_vars/all.yml` is read, THE PKI_Configuration SHALL contain an entry for `jaeger` with DNS `traces.lab`

### Requirement 5: DNS Configuration

**User Story:** As a platform operator, I want DNS rewrites for the observability services, so that `metrics.lab`, `dash.lab`, and `traces.lab` resolve to the bastion host IP.

#### Acceptance Criteria

1. WHEN the `adguard_rewrites` list in `adguard.yml` is read, THE DNS_Configuration SHALL contain a rewrite for `metrics.lab` pointing to the gateway IP
2. WHEN the `adguard_rewrites` list in `adguard.yml` is read, THE DNS_Configuration SHALL contain a rewrite for `dash.lab` pointing to the gateway IP
3. WHEN the `adguard_rewrites` list in `adguard.yml` is read, THE DNS_Configuration SHALL contain a rewrite for `traces.lab` pointing to the gateway IP

### Requirement 6: Traefik Routing

**User Story:** As a platform operator, I want Traefik HTTP routers for the observability services, so that HTTPS requests are routed to the correct ghostunnel sidecars with mTLS.

#### Acceptance Criteria

1. WHEN the `http_routers` list in `traefik.yml` is read, THE Traefik_Configuration SHALL contain a router for `victoriametrics` matching `Host(`metrics.lab`)` with mTLS enabled, routing to `https://victoriametrics:8443`
2. WHEN the `http_routers` list in `traefik.yml` is read, THE Traefik_Configuration SHALL contain a router for `grafana` matching `Host(`dash.lab`)` with mTLS enabled, routing to `https://grafana:8443`
3. WHEN the `http_routers` list in `traefik.yml` is read, THE Traefik_Configuration SHALL contain a router for `jaeger` matching `Host(`traces.lab`)` with mTLS enabled, routing to `https://jaeger:8443`

### Requirement 7: OTEL Collector Backend Configuration

**User Story:** As a platform operator, I want the OTEL Collector to export metrics and traces to VictoriaMetrics and Jaeger over mTLS, so that telemetry data flows from K8s applications to the observability backends.

#### Acceptance Criteria

1. WHEN the OTEL_Collector ConfigMap is applied, THE OTEL_Configuration SHALL define a `prometheusremotewrite` exporter targeting VictoriaMetrics at `https://metrics.lab:8443/api/v1/write` with TLS client certificate configuration
2. WHEN the OTEL_Collector ConfigMap is applied, THE OTEL_Configuration SHALL define an `otlp` exporter targeting Jaeger at `https://traces.lab:8443` with TLS client certificate configuration
3. WHEN the OTEL_Collector ConfigMap is applied, THE OTEL_Configuration SHALL replace the `debug` exporter in the `metrics` pipeline with the `prometheusremotewrite` exporter
4. WHEN the OTEL_Collector ConfigMap is applied, THE OTEL_Configuration SHALL replace the `debug` exporter in the `traces` pipeline with the `otlp` exporter
5. WHEN the OTEL_Collector Deployment is applied, THE Deployment SHALL mount TLS client certificates (cert, key, CA) from a Kubernetes Secret into the collector container
6. WHEN the OTEL_Collector ConfigMap is applied, THE OTEL_Configuration SHALL retain the `debug` exporter in the `logs` pipeline

### Requirement 8: OTEL Collector DNS Resolution

**User Story:** As a platform operator, I want the OTEL Collector in K8s to resolve `metrics.lab` and `traces.lab` via the CoreDNS → AdGuard → bastion DNS chain, so that mTLS exports reach the correct bastion services.

#### Acceptance Criteria

1. WHEN the OTEL_Collector attempts to reach `metrics.lab`, THE CoreDNS SHALL forward the `.lab` query to AdGuard on the Bastion_Host, which resolves it to the gateway IP
2. WHEN the OTEL_Collector attempts to reach `traces.lab`, THE CoreDNS SHALL forward the `.lab` query to AdGuard on the Bastion_Host, which resolves it to the gateway IP
3. WHEN the DNS resolution completes, THE Traefik_Proxy SHALL route the request to the appropriate Ghostunnel_Sidecar based on the SNI/Host header

### Requirement 9: MongoDB Deployment in Kubernetes

**User Story:** As a platform operator, I want a MongoDB deployment in the K8s `database` namespace scaled to zero replicas, so that the database is ready to activate when needed.

#### Acceptance Criteria

1. WHEN the MongoDB manifests are applied, THE MongoDB_Deployment SHALL use `replicas: 0` as the initial state so the database is provisioned but not running until activated
2. WHEN the MongoDB manifests are applied, THE MongoDB_Deployment SHALL follow the Qdrant manifest pattern with Recreate strategy, securityContext, health probes, and PVC mount
3. WHEN the MongoDB manifests are applied, THE MongoDB_Storage SHALL create a PersistentVolumeClaim using the `longhorn-hdd` StorageClass
4. WHEN the MongoDB manifests are applied, THE MongoDB_Service SHALL expose MongoDB's default port (27017) as a ClusterIP service
5. WHEN the MongoDB manifests are applied, THE MongoDB_NetworkPolicy SHALL restrict ingress to only allowed consumer namespaces
6. WHEN the MongoDB manifests are applied, THE MongoDB_Deployment SHALL reside in the `database` namespace alongside Qdrant
7. WHEN the MongoDB manifests are applied, THE MongoDB_HPA SHALL define a HorizontalPodAutoscaler that scales based on CPU utilization (target 50%) and memory utilization (target 60%)
8. WHEN the MongoDB HPA is active, THE MongoDB_HPA SHALL scale between a minimum of 1 replica and a maximum of 5 replicas

### Requirement 10: Observability Stack Integration

**User Story:** As a platform operator, I want the full observability pipeline connected end-to-end, so that K8s application telemetry flows through OTEL Collector to VictoriaMetrics (metrics) and Jaeger (traces), and Grafana can query both backends for dashboards.

#### Acceptance Criteria

1. WHEN a K8s application sends metrics via OTLP to the OTEL_Collector, THE OTEL_Collector SHALL forward the metrics to VictoriaMetrics via Prometheus Remote Write over mTLS
2. WHEN a K8s application sends traces via OTLP to the OTEL_Collector, THE OTEL_Collector SHALL forward the traces to Jaeger via OTLP over mTLS
3. WHEN Grafana loads its provisioned datasources, THE Grafana_Instance SHALL be able to query VictoriaMetrics for metrics using the Prometheus datasource type
4. WHEN Grafana loads its provisioned datasources, THE Grafana_Instance SHALL be able to query Jaeger for traces using the Jaeger datasource type
