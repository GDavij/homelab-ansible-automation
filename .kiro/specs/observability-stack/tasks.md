# Implementation Plan: Observability Stack

## Overview

Deploy VictoriaMetrics, Grafana, and Jaeger on the bastion host with ghostunnel mTLS sidecars, update the OTEL Collector in K8s to export to real backends, and add MongoDB to K8s with autoscaling. All changes follow existing patterns exactly.

## Tasks

- [x] 1. Add service versions and PKI entries
  - [x] 1.1 Add version variables to `group_vars/Gateways/versions.yml`
    - Add `victoriametrics_version: "v1.137.0-rc0"`, `grafana_version: "12.3"`, `jaeger_version: "2.15.1"`
    - _Requirements: 1.6, 2.8, 3.6_
  - [x] 1.2 Add PKI service entries to `group_vars/all.yml`
    - Add victoriametrics (metrics.lab), grafana (dash.lab), jaeger (traces.lab) to `pki_services` list
    - Follow exact pattern of existing entries (name, dns, description, ip)
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 2. Add DNS rewrites and Traefik routers
  - [x] 2.1 Add AdGuard DNS rewrites to `group_vars/Gateways/adguard.yml`
    - Add entries for metrics.lab, dash.lab, traces.lab to `adguard_rewrites` list
    - Follow exact pattern of existing rewrites (name, dns, description, ip)
    - _Requirements: 5.1, 5.2, 5.3_
  - [x] 2.2 Add Traefik HTTP routers to `group_vars/Gateways/traefik.yml`
    - Add victoriametrics, grafana, jaeger routers to `http_routers` list
    - Each with `Host()` rule, websecure entrypoint, mtls: true, loadBalancer to `https://<name>:8443`
    - Follow exact pattern of memos/trilium routers
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 3. Checkpoint - Verify group_vars changes
  - Ensure all YAML files are valid, ask the user if questions arise.

- [x] 4. Add bastion Docker Compose services
  - [x] 4.1 Add data directories to `roles/infra_gateways/tasks/main.yml`
    - Add `/opt/core/victoriametrics`, `/opt/core/grafana`, `/opt/core/jaeger` to the directory creation loop
    - _Requirements: 1.1, 2.1, 3.1_
  - [x] 4.2 Create Grafana datasources template `roles/infra_gateways/templates/grafana_datasources.yml.j2`
    - Provision VictoriaMetrics as Prometheus-type datasource (url: http://victoriametrics:8428, isDefault: true)
    - Provision Jaeger as Jaeger-type datasource (url: http://jaeger:16686)
    - _Requirements: 2.5, 2.6_
  - [x] 4.3 Add template rendering task to `roles/infra_gateways/tasks/main.yml`
    - Add task to render `grafana_datasources.yml.j2` to `/opt/core/grafana/provisioning/datasources/datasources.yml`
    - Add `/opt/core/grafana/provisioning/datasources` to directory creation loop
    - _Requirements: 2.6_
  - [x] 4.4 Add VictoriaMetrics + sidecar to `roles/infra_gateways/templates/infra_services.gateways.compose.yml.j2`
    - VictoriaMetrics: image `victoriametrics/victoria-metrics:{{ victoriametrics_version }}`, core_net, volume /opt/core/victoriametrics:/victoria-metrics-data
    - Sidecar: ghostunnel, network_mode service:victoriametrics, listen 0.0.0.0:8443, target 127.0.0.1:8428, mount PKI certs, --allow-all
    - _Requirements: 1.2, 1.3, 1.4, 1.5_
  - [x] 4.5 Add Grafana + sidecar to `roles/infra_gateways/templates/infra_services.gateways.compose.yml.j2`
    - Grafana: image `grafana/grafana:{{ grafana_version }}`, core_net, volumes for data + provisioning datasources
    - Sidecar: ghostunnel, network_mode service:grafana, listen 0.0.0.0:8443, target 127.0.0.1:3000, mount PKI certs, --allow-all
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.7_
  - [x] 4.6 Add Jaeger + sidecar to `roles/infra_gateways/templates/infra_services.gateways.compose.yml.j2`
    - Jaeger: image `jaegertracing/jaeger:{{ jaeger_version }}`, core_net, volume /opt/core/jaeger:/data, env for Badger storage
    - Sidecar: ghostunnel, network_mode service:jaeger, listen 0.0.0.0:8443, target 127.0.0.1:4318, mount PKI certs, --allow-all
    - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [x] 5. Checkpoint - Verify Ansible templates
  - Ensure all Jinja2 templates render valid YAML, ask the user if questions arise.

- [x] 6. Update OTEL Collector in Kubernetes
  - [x] 6.1 Update `observability/otel/configmap.yml` with real exporters
    - Add `prometheusremotewrite` exporter targeting `https://metrics.lab:8443/api/v1/write` with TLS config
    - Add `otlp/jaeger` exporter targeting `https://traces.lab:8443` with TLS config
    - Update metrics pipeline to use `prometheusremotewrite`, traces pipeline to use `otlp/jaeger`
    - Keep `debug` exporter in logs pipeline only
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.6_
  - [x] 6.2 Update `observability/otel/deployment.yml` with TLS cert mount
    - Add volumeMount for `/certs` from `otel-collector-tls` Secret
    - Add volume referencing the Secret
    - _Requirements: 7.5_

- [x] 7. Deploy MongoDB in Kubernetes
  - [x] 7.1 Create `database/mongodb/deployment.yml`
    - Follow Qdrant pattern: Recreate strategy, securityContext, health probes, PVC mount
    - Set `replicas: 0`, namespace `database`, ArgoCD sync-wave 3
    - _Requirements: 9.1, 9.2, 9.6_
  - [x] 7.2 Create `database/mongodb/service.yml`
    - ClusterIP service exposing port 27017
    - _Requirements: 9.4_
  - [x] 7.3 Create `database/mongodb/storage.yml`
    - PVC with `longhorn-hdd` StorageClass
    - _Requirements: 9.3_
  - [x] 7.4 Create `database/mongodb/network-policy.yml`
    - Restrict ingress to allowed consumer namespaces (follow Qdrant pattern)
    - _Requirements: 9.5_
  - [x] 7.5 Create `database/mongodb/hpa.yml`
    - HorizontalPodAutoscaler: CPU target 50%, memory target 60%, min 1, max 5
    - _Requirements: 9.7, 9.8_

- [x] 8. Final checkpoint - Verify all manifests and templates
  - Ensure all YAML files are valid, all K8s manifests have correct namespaces and labels, ask the user if questions arise.

## Notes

- All changes follow existing patterns exactly for consistency
- The OTEL Collector TLS secret (`otel-collector-tls`) must be provisioned externally (from PKI output or cert-manager)
- MongoDB starts at replicas: 0 — manually scale to 1 to activate, then HPA takes over
- Grafana connects to VictoriaMetrics and Jaeger over plain HTTP on core_net (internal Docker network)
