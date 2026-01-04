# Implementation Plan

## Overview
This implementation plan converts the homelab monitoring design into a series of actionable coding tasks. Each task builds incrementally on previous tasks, following the established Ansible and Docker patterns in the homelab infrastructure.

## Task List

- [ ] 1. Extend PKI infrastructure for monitoring services
- [ ] 1.1 Add Prometheus service certificate to pki_services
  - Add prometheus service entry to `group_vars/all.yml` pki_services array
  - Configure DNS name as `prometheus.lab` and IP as `192.168.1.77`
  - Set description as "Prometheus Monitoring Service"
  - _Requirements: 4.1_

- [ ] 1.2 Add Grafana service certificate to pki_services
  - Add grafana service entry to `group_vars/all.yml` pki_services array
  - Configure DNS name as `grafana.lab` and IP as `192.168.1.77`
  - Set description as "Grafana Visualization Service"
  - _Requirements: 4.1_

- [ ] 1.3 Add AdGuard Exporter service certificate to pki_services
  - Add adguard-exporter service entry to `group_vars/all.yml` pki_services array
  - Configure DNS name as `adguard-exporter.lab` and IP as `192.168.1.77`
  - Set description as "AdGuard Metrics Exporter Sidecar"
  - _Requirements: 4.1_

- [ ] 1.4 Add Node Exporter service certificate to pki_services
  - Add node-exporter service entry to `group_vars/all.yml` pki_services array
  - Configure DNS name as `node-exporter.lab` and IP as `192.168.1.77`
  - Set description as "System Metrics Exporter"
  - _Requirements: 4.1_

- [ ] 1.5 Verify PKI certificate generation
  - Run PKI role to generate all new monitoring service certificates
  - Verify server certificates are created in `/etc/pki/homelab/certs/`
  - Verify private keys are created in `/etc/pki/homelab/private/`
  - Test certificate validation against homelab root CA
  - _Requirements: 4.5_

- [ ] 2. Create monitoring configuration variables
- [ ] 2.1 Create monitoring variables file
  - Create `group_vars/Gateways/monitoring.yml` file
  - Define monitoring service resource limits (Prometheus 512MB, Grafana 384MB, etc.)
  - Configure retention policies (30-day maximum for Prometheus)
  - Set scrape intervals (15s for critical services, 30s for system metrics)
  - _Requirements: 12.1, 12.2, 12.4_

- [ ] 2.2 Configure network zone mappings
  - Define firewalld zone mappings in monitoring variables
  - Map underlay_network zone to 192.168.1.0/24 with services
  - Map trusted zone to docker0 and tailscale0 interfaces
  - Map external zone for internet traffic
  - _Requirements: 9.1, 9.3_

- [ ] 2.3 Set monitoring authentication variables
  - Configure Traefik authentication for monitoring dashboards
  - Set up Grafana admin credentials and session settings
  - Define monitoring service usernames and password hashes
  - _Requirements: 6.3_

- [ ] 3. Extend Docker Compose template for monitoring services
- [ ] 3.1 Add Prometheus service to Docker Compose
  - Modify `roles/infra_gateways/templates/infra_services.compose.j2`
  - Add Prometheus container with image, resource limits, and mTLS configuration
  - Mount certificate volumes from `/etc/pki/homelab/` to container paths
  - Configure persistent storage volume for `/opt/core/prometheus/data/`
  - Add Traefik labels for prometheus.lab routing
  - _Requirements: 5.1, 7.1_

- [ ] 3.2 Add Grafana service to Docker Compose
  - Add Grafana container with image, resource limits, and mTLS configuration
  - Mount certificate volumes for server and client authentication
  - Configure persistent storage volume for `/opt/core/grafana/data/`
  - Add Traefik labels for grafana.lab routing
  - _Requirements: 5.1, 7.2_

- [ ] 3.3 Add Node Exporter service to Docker Compose
  - Add Node Exporter container with minimal collector configuration
  - Mount certificate volumes for mTLS server authentication
  - Configure host network access for system metrics collection
  - Add Traefik labels for node-exporter.lab routing
  - _Requirements: 3.1, 3.2_

- [ ] 3.4 Add AdGuard Exporter sidecar service to Docker Compose
  - Add AdGuard Exporter container with deep AdGuard integration
  - Mount certificate volumes for mTLS communication with AdGuard
  - Configure access to AdGuard data volumes for log parsing
  - Add Traefik labels for adguard-exporter.lab routing
  - _Requirements: 2.1, 2.2_

- [ ] 3.5 Configure Docker networks and dependencies
  - Ensure all monitoring services connect to core_net and proxy_net
  - Set up service dependencies and startup order
  - Configure health checks for all monitoring containers
  - _Requirements: 5.5_

- [ ] 4. Create Prometheus configuration template
- [ ] 4.1 Create Prometheus main configuration template
  - Create `roles/infra_gateways/templates/prometheus.yml.j2`
  - Configure global settings with scrape and evaluation intervals
  - Set up TLS server configuration for Prometheus web interface
  - Configure external labels for homelab cluster identification
  - _Requirements: 1.1_

- [ ] 4.2 Configure Traefik metrics scraping
  - Add Traefik scrape job with mTLS server certificate authentication
  - Configure scrape target as gateway:8080 with 15-second interval
  - Set up TLS configuration with prometheus service certificate
  - Add service discovery labels for network topology
  - _Requirements: 1.1, 1.2_

- [ ] 4.3 Configure AdGuard Exporter metrics scraping
  - Add AdGuard Exporter scrape job with mTLS authentication
  - Configure scrape target as adguard-exporter:9617 with 15-second interval
  - Set up TLS configuration with prometheus service certificate
  - Add zone-based labeling for DNS metrics
  - _Requirements: 2.1, 2.3_

- [ ] 4.4 Configure Node Exporter metrics scraping
  - Add Node Exporter scrape job with mTLS authentication
  - Configure scrape target as node-exporter:9100 with 30-second interval
  - Set up minimal collector parameters (cpu, memory, disk, network, filesystem)
  - Configure TLS authentication with prometheus service certificate
  - _Requirements: 3.1, 3.2_

- [ ] 4.5 Configure retention and resource optimization
  - Set up 30-day maximum retention policy
  - Configure storage optimization for limited disk space
  - Set up memory limits and garbage collection settings
  - Configure query timeout and concurrency limits
  - _Requirements: 12.1, 12.2, 12.4_

- [ ] 5. Create Grafana configuration templates
- [ ] 5.1 Create Grafana server configuration template
  - Create `roles/infra_gateways/templates/grafana.ini.j2`
  - Configure HTTPS protocol with grafana.crt and grafana.key
  - Set up client certificate authentication with root CA
  - Configure root_url as https://grafana.lab/
  - Set resource limits and disable resource-intensive features
  - _Requirements: 4.3, 12.3_

- [ ] 5.2 Create Grafana data source configuration template
  - Create `roles/infra_gateways/templates/grafana-datasources.yml.j2`
  - Configure Prometheus data source with https://prometheus:9090
  - Set up mTLS authentication with grafana service certificate
  - Configure TLS CA certificate and server certificate validation
  - Set Prometheus as default data source
  - _Requirements: 4.3, 6.3_

- [ ] 5.3 Create Grafana dashboard provisioning configuration
  - Create dashboard provisioning configuration template
  - Set up automatic dashboard loading from templates
  - Configure dashboard update and deletion policies
  - Set up folder organization for different dashboard types
  - _Requirements: 7.2_

- [ ] 6. Implement AdGuard Exporter configuration
- [ ] 6.1 Create AdGuard Exporter main configuration template
  - Create `roles/infra_gateways/templates/adguard-exporter.yml.j2`
  - Configure AdGuard Home API connection with https://dns:443
  - Set up mTLS authentication with adguard-exporter service certificate
  - Configure API credentials and connection timeouts
  - _Requirements: 2.1_

- [ ] 6.2 Configure DNS log parsing and analysis
  - Set up DNS query log parsing from `/opt/adguardhome/data/querylog.json`
  - Configure stats database access from `/opt/adguardhome/data/stats.db`
  - Set up blocked services parsing from `/opt/adguardhome/data/blocked_services.json`
  - Enable real-time log monitoring and parsing
  - _Requirements: 2.2, 2.4_

- [ ] 6.3 Configure network zone analysis
  - Set up client IP to network zone mapping
  - Configure firewalld zone integration (underlay_network, trusted, external)
  - Enable client behavior tracking and device type detection
  - Set up geographic and logical client grouping
  - _Requirements: 9.1, 9.2, 9.4_

- [ ] 6.4 Configure domain mapping and security analysis
  - Enable domain-to-IP mapping collection and tracking
  - Set up client-domain relationship analysis
  - Configure suspicious pattern detection and scoring
  - Enable threat intelligence integration for blocked domains
  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 7. Create Traefik dynamic configuration for monitoring
- [ ] 7.1 Add Prometheus routing configuration
  - Extend `roles/infra_gateways/templates/traefik-dynamic.yml.j2`
  - Add prometheus.lab host rule and websecure entrypoint
  - Configure mTLS transport with prometheus server certificate
  - Set up load balancer configuration for prometheus:9090
  - **Enable external access for analytics and future data ingestion**
  - _Requirements: 6.1, 6.2_

- [ ] 7.2 Add Grafana routing configuration
  - Add grafana.lab host rule and websecure entrypoint
  - Configure mTLS transport with grafana server certificate
  - Set up load balancer configuration for grafana:3000
  - Add authentication middleware for dashboard access
  - _Requirements: 6.1, 6.2_

- [ ] 7.3 Add monitoring service transports
  - Create mTLS transport configurations for all monitoring services
  - Configure server certificate validation and root CA
  - Set up client certificate authentication requirements
  - Configure TLS cipher suites and protocol versions
  - _Requirements: 6.4_

- [ ] 7.4 Configure monitoring authentication middleware
  - Set up basic authentication middleware for monitoring dashboards
  - Configure user credentials and password hashes
  - Apply authentication to monitoring service routes
  - Set up bypass rules for health check endpoints
  - _Requirements: 6.3_

- [ ] 8. Implement Grafana dashboard templates
- [ ] 8.1 Create network topology dashboard
  - Create `roles/infra_gateways/templates/grafana-dashboards/network-topology.json.j2`
  - Implement interactive node graph showing all services and clients
  - Configure zone-based visualization with color-coded boundaries
  - Set up real-time traffic flow animation and health status indicators
  - Add drill-down capabilities to detailed service metrics
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 8.2 Create zone traffic analysis dashboard
  - Create `roles/infra_gateways/templates/grafana-dashboards/zone-traffic.json.j2`
  - Implement traffic matrix heat map between network zones
  - Configure client activity breakdown by zone
  - Set up bandwidth utilization graphs and top talkers analysis
  - Add security events and blocked requests visualization
  - _Requirements: 9.3, 9.4_

- [ ] 8.3 Create DNS and domain analysis dashboard
  - Create `roles/infra_gateways/templates/grafana-dashboards/dns-analysis.json.j2`
  - Implement domain access frequency visualization with client mapping
  - Configure DNS query analysis with response times and success rates
  - Set up blocked domain tracking with threat intelligence
  - Add client-domain relationship graphs
  - _Requirements: 10.1, 10.2_

- [ ] 8.4 Create service performance dashboard
  - Create `roles/infra_gateways/templates/grafana-dashboards/service-performance.json.j2`
  - Implement Traefik performance metrics with request rates and response times
  - Configure AdGuard performance with DNS resolution times and blocking effectiveness
  - Set up load balancing analysis with backend distribution and health checks
  - Add certificate monitoring with expiration tracking
  - _Requirements: 11.1, 11.3_

- [ ] 9. Update infra_gateways role tasks
- [ ] 9.1 Create monitoring data directories
  - Modify `roles/infra_gateways/tasks/main.yml`
  - Create `/opt/core/prometheus/data/` directory with proper permissions
  - Create `/opt/core/grafana/data/` directory with proper permissions
  - Set up directory ownership for monitoring service users
  - _Requirements: 7.3, 7.4_

- [ ] 9.2 Deploy Prometheus configuration
  - Add task to deploy `prometheus.yml.j2` template to `/opt/core/prometheus/`
  - Set up configuration file permissions and ownership
  - Add handler to restart Prometheus service on configuration changes
  - Validate Prometheus configuration syntax before deployment
  - _Requirements: 5.2, 5.4_

- [ ] 9.3 Deploy Grafana configuration
  - Add task to deploy `grafana.ini.j2` template to `/opt/core/grafana/`
  - Deploy `grafana-datasources.yml.j2` to provisioning directory
  - Deploy dashboard templates to Grafana dashboards directory
  - Set up configuration file permissions and ownership
  - _Requirements: 5.2, 5.4_

- [ ] 9.4 Deploy AdGuard Exporter configuration
  - Add task to deploy `adguard-exporter.yml.j2` template
  - Set up configuration file permissions and ownership
  - Add handler to restart AdGuard Exporter on configuration changes
  - Validate AdGuard Exporter configuration before deployment
  - _Requirements: 5.2, 5.4_

- [ ] 10. Implement monitoring service health checks
- [ ] 10.1 Configure Docker health checks
  - Add health check commands for all monitoring containers
  - Configure health check intervals, timeouts, and retry counts
  - Set up health check endpoints for HTTP-based services
  - Configure health check dependencies between services
  - _Requirements: 3.3_

- [ ] 10.2 Configure service dependencies and startup order
  - Set up Docker Compose depends_on for proper service startup order
  - Configure service restart policies for automatic recovery
  - Set up graceful shutdown handling for data persistence
  - Configure container resource limits and reservations
  - _Requirements: 5.3_

- [ ] 10.3 Implement graceful degradation for resource constraints
  - Configure automatic scrape interval adjustment under high load
  - Set up memory pressure detection and response
  - Implement automatic retention policy adjustment
  - Configure service priority and resource allocation
  - _Requirements: 12.5_

- [ ] 10.4 Configure monitoring service registration with Traefik
  - Ensure all monitoring services have proper Traefik labels
  - Configure automatic service discovery and health checks
  - Set up load balancer health check endpoints
  - Configure service deregistration on failure
  - _Requirements: 5.3_

- [ ] 11. Create monitoring alerting rules
- [ ] 11.1 Create Prometheus alerting rules template
  - Create `roles/infra_gateways/templates/prometheus-alerts.yml.j2`
  - Define alert rule groups for different monitoring categories
  - Configure alert evaluation intervals and rule priorities
  - Set up alert labels and annotations for proper routing
  - _Requirements: 3.3_

- [ ] 11.2 Configure resource threshold alerts
  - Define CPU usage alerts for system and container monitoring
  - Configure memory usage alerts with different severity levels
  - Set up disk space alerts with warning and critical thresholds
  - Configure network bandwidth alerts for congestion detection
  - _Requirements: 3.3_

- [ ] 11.3 Configure certificate expiration alerts
  - Set up SSL certificate expiration monitoring alerts
  - Configure different warning periods (30, 14, 7 days)
  - Set up certificate validation failure alerts
  - Configure certificate renewal reminder alerts
  - _Requirements: 1.3, 4.5_

- [ ] 11.4 Configure service health and availability alerts
  - Set up service down alerts for all monitoring components
  - Configure service response time alerts with SLA thresholds
  - Set up service error rate alerts for quality monitoring
  - Configure dependency failure alerts for cascading issues
  - _Requirements: 3.3_

- [ ] 12. Implement network topology metrics collection
- [ ] 12.1 Enhance Traefik metrics configuration
  - Configure Traefik to export enhanced metrics with client zone labels
  - Enable service-level metrics with backend health status
  - Set up request-level tracking with client IP and zone information
  - Configure load balancer distribution metrics
  - _Requirements: 8.1, 11.1_

- [ ] 12.2 Configure client zone detection and labeling
  - Implement client IP to network zone mapping in Traefik
  - Set up automatic zone detection based on source IP ranges
  - Configure zone-based labeling for all HTTP requests
  - Set up client device type detection and classification
  - _Requirements: 8.1, 9.1_

- [ ] 12.3 Set up inter-service communication tracking
  - Configure service-to-service communication metrics
  - Set up dependency mapping between services
  - Configure communication latency and error rate tracking
  - Set up service mesh visibility for internal traffic
  - _Requirements: 8.1, 8.4_

- [ ] 12.4 Implement load balancing distribution metrics
  - Configure backend server distribution tracking
  - Set up load balancer health check metrics
  - Configure failover event tracking and alerting
  - Set up scaling impact measurement and analysis
  - _Requirements: 11.1, 11.4_

- [ ] 13. Configure DNS metrics and zone analysis
- [ ] 13.1 Implement AdGuard log parsing for network topology
  - Set up real-time DNS query log parsing and analysis
  - Configure client-to-domain relationship tracking
  - Set up DNS query pattern analysis and classification
  - Configure DNS response time and success rate tracking
  - _Requirements: 9.2, 10.1_

- [ ] 13.2 Set up domain-to-IP mapping collection
  - Configure domain resolution tracking and mapping
  - Set up IP address change detection and alerting
  - Configure DNS TTL tracking and cache analysis
  - Set up domain category classification and tagging
  - _Requirements: 10.1, 10.2_

- [ ] 13.3 Configure client behavior analysis and scoring
  - Set up client activity pattern analysis
  - Configure suspicious behavior detection algorithms
  - Set up client risk scoring based on DNS queries
  - Configure behavioral anomaly detection and alerting
  - _Requirements: 9.4, 10.3_

- [ ] 13.4 Implement suspicious pattern detection metrics
  - Configure domain reputation checking and scoring
  - Set up threat intelligence integration for blocked domains
  - Configure malware and phishing domain detection
  - Set up security event correlation and analysis
  - _Requirements: 10.3_

- [ ] 14. Deploy and validate monitoring stack
- [ ] 14.1 Run Ansible playbook to deploy monitoring services
  - Execute Ansible playbook with monitoring tags
  - Deploy all monitoring configuration templates
  - Start all monitoring Docker containers
  - Verify container startup and health status
  - _Requirements: 5.2, 5.4_

- [ ] 14.2 Verify mTLS communication between services
  - Test Prometheus to Traefik mTLS scraping using service certificates
  - Test Prometheus to AdGuard Exporter mTLS scraping using service certificates
  - Test Grafana to Prometheus mTLS data source connection using service certificates
  - Verify certificate validation and authentication between all services
  - Test external access to Prometheus through Traefik for analytics
  - _Requirements: 4.2, 4.4_

- [ ] 14.3 Validate certificate deployment and rotation
  - Verify all monitoring certificates are properly deployed
  - Test certificate validation against homelab root CA
  - Verify certificate file permissions and ownership
  - Test certificate rotation and renewal process
  - _Requirements: 4.1, 4.5_

- [ ] 14.4 Test dashboard access and data visualization
  - Access Grafana dashboards via https://grafana.lab
  - Verify Prometheus data source connectivity
  - Test network topology dashboard functionality
  - Validate zone traffic analysis dashboard
  - _Requirements: 6.5, 8.5_

- [ ] 15. Final integration and optimization
- [ ] 15.1 Verify resource consumption stays within limits
  - Monitor total RAM usage of monitoring stack (max 1GB)
  - Verify individual service memory limits (Prometheus 512MB, Grafana 384MB)
  - Check CPU usage and optimize scrape intervals if needed
  - Monitor disk space usage and retention policy effectiveness
  - _Requirements: 12.1, 12.2, 12.4_

- [ ] 15.2 Test monitoring data persistence across restarts
  - Restart monitoring containers and verify data persistence
  - Test Prometheus data retention across restarts
  - Verify Grafana dashboard and configuration persistence
  - Test certificate and configuration file persistence
  - _Requirements: 7.3_

- [ ] 15.3 Validate network topology graph generation
  - Verify network topology dashboard shows all services and clients
  - Test real-time updates and traffic flow visualization
  - Validate zone-based traffic analysis and client grouping
  - Test drill-down functionality and service detail views
  - _Requirements: 8.2, 8.4_

- [ ] 15.4 Optimize scrape intervals and retention policies
  - Fine-tune scrape intervals based on resource usage
  - Optimize Prometheus retention policy for disk space
  - Configure automatic cleanup and data compression
  - Set up monitoring performance metrics and alerting
  - _Requirements: 12.2, 12.4_

## Implementation Notes

### Resource Management
- Total monitoring stack RAM limit: 1GB (Prometheus 512MB + Grafana 384MB + Node Exporter 64MB + AdGuard Exporter 40MB)
- Prometheus retention: 30 days maximum
- Scrape intervals: 15s for critical services, 30s for system metrics
- Grafana features: Disable image rendering and complex visualizations

### Security Requirements
- All inter-service communication must use mTLS with service certificates
- Certificate validation against homelab root CA required
- Services use their own certificates for both server and client authentication
- Traefik authentication middleware for dashboard access
- **Prometheus exposed through Traefik for external analytics and future data ingestion**

### Network Integration
- Use existing firewalld zones: underlay_network, trusted, external
- Docker services on trusted zone (docker0 interface)
- Client traffic through underlay_network zone
- Masquerading enabled for external DNS resolution

### Data Persistence
- Prometheus data: `/opt/core/prometheus/data/`
- Grafana data: `/opt/core/grafana/data/`
- Certificate mounting: `/etc/pki/homelab/` to container paths
- Configuration templates deployed via Ansible

### Dashboard Requirements
- Network topology with real-time updates
- Zone-based traffic analysis
- DNS query patterns and domain mapping
- Service performance and health monitoring
- Load distribution and scaling impact tracking