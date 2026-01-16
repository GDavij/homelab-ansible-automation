# Implementation Plan

- [x] 1. Modify PKI role for GhostTunnel certificate generation
  - Modify existing PKI role to support GhostTunnel proxy certificates
  - Update certificate generation templates for separate cert/key files
  - Ensure certificate format compatibility with GhostTunnel requirements
  - _Requirements: 2.1, 2.2_

- [x] 2. Add upsnap service to PKI configuration
  - Add upsnap service to pki_services configuration (using service name, not proxy name)
  - Configure DNS name (snap.lab) and IP address (192.168.1.77) as Subject Alternative Names
  - _Requirements: 2.1, 2.2_

- [x] 3. Generate upsnap certificate files
  - Generate certificate files for Upsnap GhostTunnel proxy (upsnap.crt, upsnap.key)
  - Verify certificate format and file placement for host network service
  - _Requirements: 2.1, 2.2_

- [x] 4. Add memos service to PKI configuration
  - Add memos to pki_services configuration (using service name, not proxy name)
  - Configure DNS name (daily.lab) and IP address as SANs
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 5. Add maybe-finance service to PKI configuration
  - Add maybe-finance to pki_services configuration (using service name, not proxy name)
  - Configure DNS name (finance.lab) and IP address as SANs
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 6. Add trilium service to PKI configuration
  - Add trilium to pki_services configuration (using service name, not proxy name)
  - Configure DNS name (notes.lab) and IP address as SANs
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 7. Generate application certificate files
  - Generate certificate files for each application's GhostTunnel sidecar (memos.crt, maybe-finance.crt, trilium.crt)
  - Verify certificate format and file placement for all application proxies
  - _Requirements: 2.1, 2.2, 2.3_

- [X] 8. Create Upsnap configuration file structure
  - Create group_vars/Gateways/upsnap.yml configuration file
  - Define upsnap_machines variable structure for Monster Machine
  - _Requirements: 3.1_

- [x] 8.1 Configure Monster Machine in Upsnap
  - Set up Monster Machine configuration (IP: 192.168.1.90, MAC, SSH key)
  - Configure machine-specific settings for Wake-on-LAN
  - _Requirements: 3.1_

- [x] 9. Create Upsnap application configuration template
  - Create Upsnap application configuration template
  - Configure database path, web port, scan range settings
  - _Requirements: 3.1_

- [x] 10. Implement Upsnap auto-discovery configuration
  - Implement auto-discovery and SSH timeout configuration
  - Configure network scanning parameters
  - _Requirements: 3.1_

- [x] 11. Extend infra_services template for Upsnap container
  - Extend existing infra_services.compose.j2 template to include Upsnap service only
  - Configure basic Upsnap container definition without Traefik labels (uses static config)
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [x] 12. Configure Upsnap GhostTunnel host network proxy
  - Implement Upsnap container with host network GhostTunnel pattern
  - Configure network_mode: host and container dependencies
  - Configure port 8443 for Upsnap mTLS access
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [x] 13. Add certificate volume mounts for Upsnap
  - Add certificate volume mounts for Upsnap GhostTunnel proxy
  - Configure certificate file paths (upsnap.crt, upsnap.key) and permissions for host network service
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [x] 14. Configure firewall rules for Upsnap host network service
  - Configure firewalld rules to allow mTLS port (8443) and block HTTP port (8090)
  - Implement firewall integration for Upsnap service security only (leave AdGuard unchanged)
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [x] 15. Configure Upsnap with auto-generated machine configuration
  - Configure Upsnap with auto-generated machine configuration
  - Implement configuration file mounting and environment variables
  - Update Monster Machine IP to 192.168.1.50 for WoL functionality
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [ ] 16. Create apps_gateways role directory structure
  - Create new apps_gateways role directory structure
  - Set up tasks, templates, and handlers directories
  - _Requirements: 6.1, 7.1, 8.1_

- [ ] 17. Implement apps_gateways main task orchestration
  - Implement main.yml task orchestration
  - Configure task includes and role dependencies
  - _Requirements: 6.1, 7.1, 8.1_

- [ ] 18. Create apps_services Docker Compose template
  - Create apps_services.compose.j2 template for application services
  - Set up basic template structure and variables
  - _Requirements: 6.1, 7.1, 8.1_

- [ ] 19. Configure application data volume directories
  - Configure directory creation for application data volumes
  - Set up proper permissions and ownership
  - _Requirements: 6.1, 7.1, 8.1_

- [ ] 20. Implement Memos container configuration
  - Implement Memos container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - _Requirements: 6.2, 6.3_

- [ ] 21. Configure Memos GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:memos
  - Set up container networking and dependencies
  - _Requirements: 6.2, 6.3_

- [ ] 22. Add certificate volume mounts for Memos
  - Set up certificate volume mounts for memos-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 6.2, 6.3_

- [ ] 23. Configure Memos data persistence
  - Configure data persistence volume for /var/opt/memos
  - Set up proper volume mounting and permissions
  - _Requirements: 6.2, 6.3_

- [ ] 24. Implement Maybe Finance container configuration
  - Implement Maybe Finance container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - _Requirements: 7.2, 7.3_

- [ ] 25. Configure Maybe Finance GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:maybe-finance
  - Set up container networking and dependencies
  - _Requirements: 7.2, 7.3_

- [ ] 26. Add certificate volume mounts for Maybe Finance
  - Set up certificate volume mounts for maybe-finance-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 7.2, 7.3_

- [ ] 27. Configure Maybe Finance data persistence
  - Configure data persistence volume for /app/data
  - Set up proper volume mounting and permissions
  - _Requirements: 7.2, 7.3_

- [ ] 28. Implement Trilium container configuration
  - Implement Trilium container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - _Requirements: 8.2, 8.3_

- [ ] 29. Configure Trilium GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:trilium
  - Set up container networking and dependencies
  - _Requirements: 8.2, 8.3_

- [ ] 30. Add certificate volume mounts for Trilium
  - Set up certificate volume mounts for trilium-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 8.2, 8.3_

- [ ] 31. Configure Trilium data persistence
  - Configure data persistence volume for /home/node/trilium-data
  - Set up proper volume mounting and permissions
  - _Requirements: 8.2, 8.3_

- [ ] 32. Create ztn_tcp_labels macro for TCP routing
  - Create ztn_tcp_labels macro for TCP routing with SNI (Docker network services only)
  - Implement macro logic for dynamic TCP service configuration
  - _Requirements: 9.1, 9.3_

- [ ] 33. Update Traefik static configuration for host network services
  - Add static TCP router configuration for Upsnap (snap.lab -> 192.168.1.77:8443)
  - Configure TCP routing in traefik-dynamic.yml for host network GhostTunnel
  - Ensure Traefik can route from Docker network to host network service
  - _Requirements: 9.1, 9.3_

- [ ] 34. Configure SSL passthrough for GhostTunnel services
  - Configure SSL passthrough for both static (host network) and dynamic (Docker network) services
  - Set up TLS configuration and SNI routing for hybrid configuration
  - _Requirements: 9.1, 9.3_

- [ ] 35. Configure certificate deployment for GhostTunnel containers
  - Configure certificate deployment for GhostTunnel containers
  - Set up certificate file distribution and mounting
  - _Requirements: 2.5, 2.6_

- [ ] 36. Implement container restart logic for certificate updates
  - Implement container restart logic for certificate updates
  - Configure automatic container restart on certificate changes
  - _Requirements: 2.5, 2.6_

- [ ] 37. Ensure certificate authority validation in GhostTunnel
  - Ensure certificate authority validation in GhostTunnel configuration
  - Configure CA certificate distribution and validation
  - _Requirements: 2.5, 2.6_

- [ ] 38. Implement health check configuration for GhostTunnel services
  - Implement health check configuration for GhostTunnel services
  - Configure container health monitoring and reporting
  - _Requirements: 9.4, 9.5_

- [ ] 39. Configure Traefik service discovery for application containers
  - Configure Traefik service discovery for application containers
  - Set up automatic service registration and routing
  - _Requirements: 9.4, 9.5_

- [ ] 40. Implement service removal logic for unavailable services
  - Implement service removal logic for unavailable services
  - Configure automatic cleanup of failed or stopped services
  - _Requirements: 9.4, 9.5_

- [ ] 41. Validate pki_services configuration mapping
  - Validate pki_services configuration mapping to service discovery
  - Implement configuration consistency checks
  - _Requirements: 10.1, 10.5_

- [ ] 42. Ensure DNS names and IP addresses are correctly mapped
  - Ensure DNS names and IP addresses are correctly mapped
  - Validate service discovery configuration consistency
  - _Requirements: 10.1, 10.5_

- [ ] 43. Implement configuration validation tasks
  - Implement configuration validation tasks
  - Add automated checks for configuration consistency
  - _Requirements: 10.1, 10.5_

- [ ] 43.1. Implement configuration syntax validation
  - Source virtual environment: `source .venv/bin/activate`
  - Validate Ansible playbook syntax: `ansible-playbook site.yml --syntax-check`
  - Validate Docker Compose template syntax: `docker-compose -f templates/infra_services.compose.j2 config --quiet`
  - Validate YAML configuration files: `python -c "import yaml; yaml.safe_load(open('group_vars/all.yml'))"`
  - Check Jinja2 template syntax for all templates
  - _Requirements: Professional execution_

- [ ] 43.2. Implement pre-deployment validation checks
  - Source virtual environment: `source .venv/bin/activate`
  - Verify required directories exist: `/opt/core/upsnap`, `/opt/apps/memos`, `/opt/apps/maybe`, `/opt/apps/trilium`
  - Check disk space requirements: `df -h /opt/`
  - Validate network connectivity to target hosts: `ansible all -m ping`
  - Verify Docker daemon is running: `ansible all -m service -a "name=docker state=started"`
  - Check firewalld service status: `ansible all -m service -a "name=firewalld state=started"`
  - _Requirements: Professional execution_

- [ ] 43.3. Create deployment logging and monitoring
  - Source virtual environment: `source .venv/bin/activate`
  - Configure Ansible logging: `export ANSIBLE_LOG_PATH=/tmp/ghosttunnel-deployment-$(date +%Y%m%d-%H%M%S).log`
  - Set up deployment progress tracking with timestamps
  - Configure verbose output for debugging: `export ANSIBLE_STDOUT_CALLBACK=debug`
  - Create deployment status checkpoints throughout the process
  - _Requirements: Professional execution_

- [ ] 43.4. Implement idempotency verification
  - Source virtual environment: `source .venv/bin/activate`
  - Run deployment twice to verify idempotency: `ansible-playbook site.yml --check --diff`
  - Verify no changes occur on second run
  - Test configuration drift detection
  - Validate that repeated deployments don't break existing services
  - _Requirements: Professional execution_

- [ ] 43.5. Create service dependency verification
  - Source virtual environment: `source .venv/bin/activate`
  - Verify PKI infrastructure is functional before certificate generation
  - Check Traefik is running before configuring routing
  - Validate Docker networks exist before container deployment
  - Ensure firewalld is configured before applying rules
  - Test DNS resolution for all service domains (snap.lab, daily.lab, finance.lab, notes.lab)
  - _Requirements: Professional execution_

- [ ] 43.6. Implement security validation checks
  - Source virtual environment: `source .venv/bin/activate`
  - Verify certificate permissions are restrictive (600 for private keys)
  - Check that no services are exposed without mTLS protection
  - Validate firewall rules block unauthorized access
  - Ensure GhostTunnel containers run with appropriate security contexts
  - Verify no plain HTTP endpoints are accessible externally
  - _Requirements: Professional execution_

- [ ] 43.7. Create performance baseline measurements
  - Source virtual environment: `source .venv/bin/activate`
  - Measure baseline system resource usage before deployment
  - Monitor CPU and memory usage during deployment
  - Test network latency through mTLS proxy vs direct connection
  - Measure certificate validation overhead
  - Document performance impact of GhostTunnel proxy layer
  - _Requirements: Professional execution_

- [ ] 43.8. Implement health check automation
  - Source virtual environment: `source .venv/bin/activate`
  - Create automated health check scripts for all services
  - Implement container health monitoring with proper exit codes
  - Set up service availability monitoring endpoints
  - Configure automatic alerting for service failures
  - Create health check dashboard or status page
  - _Requirements: Professional execution_

- [ ] 43.9. Create documentation and runbooks
  - Source virtual environment: `source .venv/bin/activate`
  - Document all configuration changes made to existing systems
  - Create troubleshooting guide for common issues
  - Document certificate renewal procedures
  - Create service restart procedures for maintenance
  - Document firewall rule management
  - Create client certificate distribution guide
  - _Requirements: Professional execution_

- [ ] 44. Test PKI certificate generation and deployment
  - Source virtual environment: `source .venv/bin/activate`
  - Run PKI role to generate all certificates: `ansible-playbook site.yml --tags "pki" --limit bastion_automation`
  - Verify certificate files exist in .pki_output/ directory
  - Check certificate validity: `openssl x509 -in .pki_output/upsnap.crt -text -noout`
  - Validate Subject Alternative Names for all service certificates
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 45. Test Upsnap infrastructure service deployment
  - Source virtual environment: `source .venv/bin/activate`
  - Deploy Upsnap infrastructure: `ansible-playbook site.yml --tags "infra_gateways" --limit bastion_automation`
  - Verify containers are running: `docker ps | grep upsnap`
  - Check Upsnap container logs: `docker logs upsnap`
  - Check GhostTunnel container logs: `docker logs upsnap-ghosttunnel`
  - Test host network binding: `netstat -tlnp | grep 8443`
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [ ] 46. Test Upsnap mTLS connectivity and WoL functionality
  - Source virtual environment: `source .venv/bin/activate`
  - Test mTLS connection with client certificate: `curl --cert client.crt --key client.key --cacert ca.crt https://snap.lab:8443`
  - Test connection rejection without certificate: `curl -k https://snap.lab:8443` (should fail)
  - Verify firewall rules: `firewall-cmd --list-ports`
  - Test Wake-on-LAN to Monster Machine (192.168.1.50) through Upsnap interface
  - Check Upsnap auto-configuration with Monster Machine settings
  - _Requirements: 1.3, 1.4, 1.5, 3.1_

- [ ] 47. Test Traefik static configuration for host network routing
  - Source virtual environment: `source .venv/bin/activate`
  - Verify Traefik static configuration: `docker exec traefik cat /etc/traefik/dynamic/traefik-dynamic.yml`
  - Test SNI routing: `curl --cert client.crt --key client.key --cacert ca.crt --resolve snap.lab:8443:192.168.1.77 https://snap.lab:8443`
  - Check Traefik logs for TCP routing: `docker logs traefik | grep snap.lab`
  - Verify SSL passthrough is working correctly
  - _Requirements: 9.1, 9.3_

- [ ] 48. Test application services deployment (Memos, Maybe Finance, Trilium)
  - Source virtual environment: `source .venv/bin/activate`
  - Deploy application services: `ansible-playbook site.yml --tags "apps_gateways" --limit bastion_automation`
  - Verify all application containers are running: `docker ps | grep -E "(memos|maybe-finance|trilium)"`
  - Check sidecar GhostTunnel containers: `docker ps | grep sidecar`
  - Verify network_mode configuration: `docker inspect memos-sidecar | grep NetworkMode`
  - Test shared network stack: `docker exec memos netstat -tlnp | grep 8443`
  - _Requirements: 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 8.1, 8.2, 8.3_

- [ ] 49. Test application mTLS connectivity
  - Source virtual environment: `source .venv/bin/activate`
  - Test Memos mTLS: `curl --cert client.crt --key client.key --cacert ca.crt https://daily.lab:8443`
  - Test Maybe Finance mTLS: `curl --cert client.crt --key client.key --cacert ca.crt https://finance.lab:8443`
  - Test Trilium mTLS: `curl --cert client.crt --key client.key --cacert ca.crt https://notes.lab:8443`
  - Verify certificate validation failures: `curl -k https://daily.lab:8443` (should fail)
  - Check application accessibility only via localhost from sidecar
  - _Requirements: 1.3, 1.4, 1.5_

- [ ] 50. Test Traefik service discovery for Docker network services
  - Source virtual environment: `source .venv/bin/activate`
  - Verify Traefik discovers application services: `docker exec traefik wget -qO- http://localhost:8080/api/tcp/routers`
  - Check TCP router configuration for each application
  - Test SNI-based routing for all applications
  - Verify health checks and service availability monitoring
  - _Requirements: 9.1, 9.2, 9.4, 9.5_

- [ ] 51. Test certificate authority validation and client authentication
  - Source virtual environment: `source .venv/bin/activate`
  - Test with valid client certificate: All services should accept connection
  - Test with invalid/expired certificate: All services should reject connection
  - Test with wrong CA certificate: All services should reject connection
  - Verify GhostTunnel logs show authentication success/failure
  - Check certificate validation against homelab CA
  - _Requirements: 2.6, 1.3, 1.4_

- [ ] 52. Test container restart and certificate deployment
  - Source virtual environment: `source .venv/bin/activate`
  - Regenerate certificates: `ansible-playbook site.yml --tags "pki" --extra-vars "force_cert_regen=true"`
  - Verify containers restart automatically after certificate update
  - Test new certificates are loaded correctly
  - Verify mTLS connections work with new certificates
  - _Requirements: 2.5_

- [ ] 53. Test firewall integration and security
  - Source virtual environment: `source .venv/bin/activate`
  - Verify firewall allows mTLS port 8443: `curl --cert client.crt --key client.key --cacert ca.crt https://192.168.1.77:8443`
  - Verify firewall blocks direct HTTP port 8090: `curl http://192.168.1.77:8090` (should fail)
  - Test firewall rules are correctly applied
  - Verify only mTLS traffic is allowed to host network services
  - _Requirements: 1.1, 1.2_

- [ ] 54. Test end-to-end functionality and integration
  - Source virtual environment: `source .venv/bin/activate`
  - Test complete workflow: Client → Traefik → GhostTunnel → Application
  - Verify all services are accessible via their DNS names (snap.lab, daily.lab, finance.lab, notes.lab)
  - Test service isolation: Applications only accessible via GhostTunnel
  - Verify Wake-on-LAN functionality through Upsnap
  - Test data persistence for all applications
  - _Requirements: All requirements_

- [ ] 55. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.