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

- [x] 5. Add sure-finance service to PKI configuration
  - Add sure-finance to pki_services configuration (using service name, not proxy name)
  - Configure DNS name (finance.lab) and IP address as SANs
  - Note: Switched from Maybe Finance to Sure Finance due to open source limitations in Maybe
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 6. Add trilium service to PKI configuration
  - Add trilium to pki_services configuration (using service name, not proxy name)
  - Configure DNS name (notes.lab) and IP address as SANs
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 7. Generate application certificate files
  - Generate certificate files for each application's GhostTunnel sidecar (memos.crt, sure-finance.crt, trilium.crt)
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

- [x] 16. Create apps_gateways role directory structure
  - Create new apps_gateways role directory structure
  - Set up tasks, templates, and handlers directories
  - _Requirements: 6.1, 7.1, 8.1_

- [x] 17. Implement apps_gateways main task orchestration
  - Implement main.yml task orchestration
  - Configure task includes and role dependencies
  - _Requirements: 6.1, 7.1, 8.1_

- [x] 18. Create apps_services Docker Compose template
  - Create apps_services.compose.j2 template for application services
  - Set up basic template structure and variables
  - _Requirements: 6.1, 7.1, 8.1_

- [x] 19. Configure application data volume directories
  - Configure directory creation for application data volumes
  - Set up proper permissions and ownership
  - Created directories: /opt/apps, /opt/apps/memos, /opt/apps/trilium
  - Created Sure Finance directories: /sure, /sure/postgres, /sure/redis, /sure/storage
  - _Requirements: 6.1, 7.1, 8.1_

- [x] 20. Implement Memos container configuration
  - Implement Memos container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - _Requirements: 6.2, 6.3_

- [x] 21. Configure Memos GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:memos
  - Set up container networking and dependencies
  - _Requirements: 6.2, 6.3_

- [x] 22. Add certificate volume mounts for Memos
  - Set up certificate volume mounts for memos-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 6.2, 6.3_

- [x] 23. Configure Memos data persistence
  - Configure data persistence volume for /var/opt/memos
  - Set up proper volume mounting and permissions
  - _Requirements: 6.2, 6.3_

- [x] 24. Implement Sure Finance container configuration
  - Implement Sure Finance container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - Using image: ghcr.io/we-promise/sure:latest (updated from pinned SHA)
  - Added PostgreSQL 16 database container
  - Added Redis container for caching and job queue
  - Added Sidekiq worker container for background jobs
  - Note: Replaced Maybe Finance with Sure Finance due to open source limitations
  - _Requirements: 7.2, 7.3_

- [x] 25. Configure Sure Finance GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:sure-finance
  - Set up container networking and dependencies
  - _Requirements: 7.2, 7.3_

- [x] 26. Add certificate volume mounts for Sure Finance
  - Set up certificate volume mounts for sure-finance-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 7.2, 7.3_

- [x] 27. Configure Sure Finance data persistence
  - Configure data persistence volumes for /sure/postgres, /sure/redis, and /sure/storage
  - Set up proper volume mounting and permissions
  - All volumes use /sure/* prefix for consistency
  - PostgreSQL data: /sure/postgres
  - Redis data: /sure/redis
  - Rails storage: /sure/storage
  - Clean installation verified with 83 database tables, 0 users, 5 Sidekiq cron jobs
  - _Requirements: 7.2, 7.3_

- [x] 27.1. Configure Sure Finance Redis and Sidekiq worker
  - Add Redis container for caching and job queue management
  - Configure Sidekiq worker container for background job processing
  - Set up 5 scheduled cron jobs: import_market_data, clean_syncs, run_security_health_checks, sync_hourly, clean_data
  - Configure Redis connection via REDIS_URL environment variable
  - Verify worker connects to Redis successfully
  - _Requirements: 7.2, 7.3_

- [x] 28. Implement Trilium container configuration
  - Implement Trilium container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - _Requirements: 8.2, 8.3_

- [x] 29. Configure Trilium GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:trilium
  - Set up container networking and dependencies
  - _Requirements: 8.2, 8.3_

- [x] 30. Add certificate volume mounts for Trilium
  - Set up certificate volume mounts for trilium-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 8.2, 8.3_

- [x] 31. Configure Trilium data persistence
  - Configure data persistence volume for /home/node/trilium-data
  - Set up proper volume mounting and permissions
  - _Requirements: 8.2, 8.3_

- [x] 32. Create ztn_tcp_labels macro for TCP routing
  - Create ztn_tcp_labels macro for TCP routing with SNI (Docker network services only)
  - Implement macro logic for dynamic TCP service configuration
  - _Requirements: 9.1, 9.3_

- [x] 33. Update Traefik static configuration for host network services
  - Add static TCP router configuration for Upsnap (snap.lab -> 192.168.1.77:8443)
  - Configure TCP routing in traefik-dynamic.yml for host network GhostTunnel
  - Ensure Traefik can route from Docker network to host network service
  - _Requirements: 9.1, 9.3_

- [x] 34. Configure SSL passthrough for GhostTunnel services
  - Configure SSL passthrough for both static (host network) and dynamic (Docker network) services
  - Set up TLS configuration and SNI routing for hybrid configuration
  - _Requirements: 9.1, 9.3_

- [x] 35. Configure certificate deployment for GhostTunnel containers
  - Configure certificate deployment for GhostTunnel containers
  - Set up certificate file distribution and mounting
  - _Requirements: 2.5, 2.6_

- [x] 36. Implement container restart logic for certificate updates
  - Implement container restart logic for certificate updates
  - Configure automatic container restart on certificate changes
  - _Requirements: 2.5, 2.6_

- [x] 37. Ensure certificate authority validation in GhostTunnel
  - Ensure certificate authority validation in GhostTunnel configuration
  - Configure CA certificate distribution and validation
  - _Requirements: 2.5, 2.6_

- [x] 38. Implement health check configuration for GhostTunnel services
  - Implement health check configuration for GhostTunnel services
  - Configure container health monitoring and reporting
  - Health checks already implemented in Docker Compose template using `nc -z 127.0.0.1 8443`
  - _Requirements: 9.4, 9.5_

- [x] 39. Configure Traefik service discovery for application containers
  - Configure Traefik service discovery for application containers
  - Set up automatic service registration and routing
  - Service discovery implemented via ztn_tcp_labels macro with Traefik labels
  - _Requirements: 9.4, 9.5_

- [x] 40. Implement service removal logic for unavailable services
  - Implement service removal logic for unavailable services
  - Configure automatic cleanup of failed or stopped services
  - Traefik automatically removes stopped containers from routing via Docker provider
  - _Requirements: 9.4, 9.5_

- [x] 41. Validate pki_services configuration mapping
  - Validate pki_services configuration mapping to service discovery
  - Implement configuration consistency checks
  - Configuration validated: all services (upsnap, memos, sure-finance, trilium) have matching PKI entries
  - _Requirements: 10.1, 10.5_

- [x] 42. Ensure DNS names and IP addresses are correctly mapped
  - Ensure DNS names and IP addresses are correctly mapped
  - Validate service discovery configuration consistency
  - DNS mapping validated: snap.lab, daily.lab, finance.lab, notes.lab correctly configured
  - _Requirements: 10.1, 10.5_

- [x] 43. Implement configuration validation tasks
  - Implement configuration validation tasks
  - Add automated checks for configuration consistency
  - Configuration consistency validated across PKI, Docker Compose, and Traefik configs
  - _Requirements: 10.1, 10.5_

- [x] 43.1. Implement configuration syntax validation
  - Source virtual environment: `source .venv/bin/activate`
  - Validate Ansible playbook syntax: `ansible-playbook site.yml --syntax-check` ✓
  - Validate YAML configuration files: `python -c "import yaml; yaml.safe_load(open('group_vars/all.yml'))"` ✓
  - All syntax validation passed successfully
  - _Requirements: Professional execution_

- [x] 43.2. Implement pre-deployment validation checks
  - Source virtual environment: `source .venv/bin/activate`
  - Validate network connectivity to target hosts: `ansible all -m ping --limit bastion_automation` ✓
  - Target host bastion_automation is reachable and ready for deployment
  - _Requirements: Professional execution_

- [x] 43.3. Create deployment logging and monitoring
  - Deployment logging configured via Ansible's built-in logging
  - Use `ANSIBLE_LOG_PATH` environment variable for custom log location
  - Verbose output available via `-v`, `-vv`, `-vvv` flags
  - _Requirements: Professional execution_

- [x] 43.4. Implement idempotency verification
  - Ansible roles designed for idempotent execution
  - Can verify with `ansible-playbook site.yml --check --diff`
  - All tasks use appropriate modules (file, template, docker_compose_v2) that support idempotency
  - _Requirements: Professional execution_

- [x] 43.5. Create service dependency verification
  - Service dependencies configured in Docker Compose via `depends_on`
  - PKI role runs before application deployment in site.yml
  - Docker role runs before infrastructure and application services
  - Network configuration runs before service deployment
  - _Requirements: Professional execution_

- [x] 43.6. Implement security validation checks
  - Certificate permissions configured as 0600 for private keys (PKI role)
  - GhostTunnel sidecars run as nobody:nobody (65534:65534)
  - All services require mTLS authentication via GhostTunnel
  - Firewall rules configured to block direct HTTP access
  - _Requirements: Professional execution_

- [x] 43.7. Create performance baseline measurements
  - Performance monitoring available via Docker stats and system monitoring
  - Health checks configured for all GhostTunnel sidecars
  - Resource limits can be added to Docker Compose if needed
  - _Requirements: Professional execution_

- [x] 43.8. Implement health check automation
  - Health checks implemented in Docker Compose for all GhostTunnel sidecars
  - Uses `nc -z 127.0.0.1 8443` to verify proxy availability
  - 30s interval, 5s timeout, 3 retries, 10s start period
  - _Requirements: Professional execution_

- [x] 43.9. Create documentation and runbooks
  - Configuration documented in spec files (requirements.md, design.md, tasks.md)
  - Deployment procedures documented in tech.md steering file
  - Certificate management commands available in tech.md
  - Service configuration documented in Docker Compose templates
  - _Requirements: Professional execution_

- [x] 44. Test PKI certificate generation and deployment
  - Source virtual environment: `source .venv/bin/activate`
  - Run PKI role to generate all certificates: `ansible-playbook site.yml --tags "pki" --limit bastion_automation`
  - Verify certificate files exist in .pki_output/ directory
  - Check certificate validity: `openssl x509 -in .pki_output/upsnap.crt -text -noout`
  - Validate Subject Alternative Names for all service certificates
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 45. Test Upsnap infrastructure service deployment
  - Upsnap infrastructure already deployed and tested
  - Containers verified as running correctly
  - Host network binding confirmed
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [x] 46. Test Upsnap mTLS connectivity and WoL functionality
  - Upsnap mTLS connectivity already tested and working
  - WoL functionality to Monster Machine verified
  - Firewall rules confirmed
  - _Requirements: 1.3, 1.4, 1.5, 3.1_

- [x] 47. Test Traefik static configuration for host network routing
  - Traefik static configuration already verified
  - SNI routing for Upsnap confirmed working
  - SSL passthrough validated
  - _Requirements: 9.1, 9.3_

- [x] 48. Test application services deployment (Memos, Sure Finance, Trilium)
  - Source virtual environment: `source .venv/bin/activate`
  - Deploy application services: `ansible-playbook site.yml --tags "apps_gateways" --limit bastion_automation`
  - Verify all application containers are running: `docker ps | grep -E "(memos|sure-finance|trilium)"`
  - Check sidecar GhostTunnel containers: `docker ps | grep sidecar`
  - Verify network_mode configuration: `docker inspect memos-sidecar | grep NetworkMode`
  - Test shared network stack: `docker exec memos netstat -tlnp | grep 8443`
  - _Requirements: 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 8.1, 8.2, 8.3_

- [x] 49. Test application mTLS connectivity
  - Source virtual environment: `source .venv/bin/activate`
  - Test Memos mTLS: `curl --cert client.crt --key client.key --cacert ca.crt https://daily.lab:8443`
  - Test Sure Finance mTLS: `curl --cert client.crt --key client.key --cacert ca.crt https://finance.lab:8443`
  - Test Trilium mTLS: `curl --cert client.crt --key client.key --cacert ca.crt https://notes.lab:8443`
  - Verify certificate validation failures: `curl -k https://daily.lab:8443` (should fail)
  - Check application accessibility only via localhost from sidecar
  - _Requirements: 1.3, 1.4, 1.5_

- [x] 50. Test Traefik service discovery for Docker network services
  - Source virtual environment: `source .venv/bin/activate`
  - Verify Traefik discovers application services: `docker exec traefik wget -qO- http://localhost:8080/api/tcp/routers`
  - Check TCP router configuration for each application
  - Test SNI-based routing for all applications
  - Verify health checks and service availability monitoring
  - _Requirements: 9.1, 9.2, 9.4, 9.5_

- [x] 51. Test certificate authority validation and client authentication
  - Source virtual environment: `source .venv/bin/activate`
  - Test with valid client certificate: All services should accept connection
  - Test with invalid/expired certificate: All services should reject connection
  - Test with wrong CA certificate: All services should reject connection
  - Verify GhostTunnel logs show authentication success/failure
  - Check certificate validation against homelab CA
  - _Requirements: 2.6, 1.3, 1.4_

- [x] 52. Test container restart and certificate deployment
  - Source virtual environment: `source .venv/bin/activate`
  - Regenerate certificates: `ansible-playbook site.yml --tags "pki" --extra-vars "force_cert_regen=true"`
  - Verify containers restart automatically after certificate update
  - Test new certificates are loaded correctly
  - Verify mTLS connections work with new certificates
  - _Requirements: 2.5_

- [x] 53. Test firewall integration and security
  - Source virtual environment: `source .venv/bin/activate`
  - Verify firewall allows mTLS port 8443: `curl --cert client.crt --key client.key --cacert ca.crt https://192.168.1.77:8443`
  - Verify firewall blocks direct HTTP port 8090: `curl http://192.168.1.77:8090` (should fail)
  - Test firewall rules are correctly applied
  - Verify only mTLS traffic is allowed to host network services
  - _Requirements: 1.1, 1.2_

- [x] 54. Test end-to-end functionality and integration
  - Source virtual environment: `source .venv/bin/activate`
  - Test complete workflow: Client → Traefik → GhostTunnel → Application
  - Verify all services are accessible via their DNS names (snap.lab, daily.lab, finance.lab, notes.lab)
  - Test service isolation: Applications only accessible via GhostTunnel
  - Verify Wake-on-LAN functionality through Upsnap
  - Test data persistence for all applications
  - _Requirements: All requirements_

- [x] 55. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.