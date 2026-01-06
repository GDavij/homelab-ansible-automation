# Implementation Plan

- [ ] 1. Modify PKI role for GhostTunnel certificate generation
  - Modify existing PKI role to support GhostTunnel proxy certificates
  - Update certificate generation templates for separate cert/key files
  - Ensure certificate format compatibility with GhostTunnel requirements
  - _Requirements: 2.1, 2.2_

- [ ] 2. Add upsnap-proxy service to PKI configuration
  - Add upsnap-proxy service to pki_services configuration
  - Configure DNS name (snap.lab) and IP address (192.168.1.77) as Subject Alternative Names
  - _Requirements: 2.1, 2.2_

- [ ] 3. Generate upsnap-proxy certificate files
  - Generate certificate files for Upsnap GhostTunnel sidecar
  - Verify certificate format and file placement
  - _Requirements: 2.1, 2.2_

- [ ] 4. Add excalidraw-proxy service to PKI configuration
  - Add excalidraw-proxy to pki_services configuration
  - Configure DNS name (draw.lab) and IP address as SANs
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 5. Add memos-proxy service to PKI configuration
  - Add memos-proxy to pki_services configuration
  - Configure DNS name (daily.lab) and IP address as SANs
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 6. Add maybe-finance-proxy service to PKI configuration
  - Add maybe-finance-proxy to pki_services configuration
  - Configure DNS name (finance.lab) and IP address as SANs
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 7. Generate application proxy certificate files
  - Generate certificate files for each application's GhostTunnel sidecar
  - Verify certificate format and file placement for all application proxies
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 8. Create Upsnap configuration file structure
  - Create group_vars/Gateways/upsnap.yml configuration file
  - Define upsnap_machines variable structure for Monster Machine
  - _Requirements: 3.1_

- [ ] 9. Configure Monster Machine in Upsnap
  - Set up Monster Machine configuration (IP: 192.168.1.90, MAC, SSH key)
  - Configure machine-specific settings for Wake-on-LAN
  - _Requirements: 3.1_

- [ ] 10. Create Upsnap application configuration template
  - Create Upsnap application configuration template
  - Configure database path, web port, scan range settings
  - _Requirements: 3.1_

- [ ] 11. Implement Upsnap auto-discovery configuration
  - Implement auto-discovery and SSH timeout configuration
  - Configure network scanning parameters
  - _Requirements: 3.1_

- [ ] 12. Extend infra_services template for Upsnap container
  - Extend existing infra_services.compose.j2 template to include Upsnap service
  - Configure basic Upsnap container definition
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [ ] 13. Configure Upsnap GhostTunnel sidecar
  - Implement Upsnap container with sidecar GhostTunnel pattern
  - Configure network_mode and container dependencies
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [ ] 14. Add certificate volume mounts for Upsnap
  - Add certificate volume mounts for GhostTunnel sidecar
  - Configure certificate file paths and permissions
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [ ] 15. Configure Upsnap with auto-generated machine configuration
  - Configure Upsnap with auto-generated machine configuration
  - Implement configuration file mounting and environment variables
  - _Requirements: 1.1, 1.2, 4.1, 4.2, 4.3_

- [ ] 16. Create apps_gateways role directory structure
  - Create new apps_gateways role directory structure
  - Set up tasks, templates, and handlers directories
  - _Requirements: 5.1, 6.1, 7.1_

- [ ] 17. Implement apps_gateways main task orchestration
  - Implement main.yml task orchestration
  - Configure task includes and role dependencies
  - _Requirements: 5.1, 6.1, 7.1_

- [ ] 18. Create apps_services Docker Compose template
  - Create apps_services.compose.j2 template for application services
  - Set up basic template structure and variables
  - _Requirements: 5.1, 6.1, 7.1_

- [ ] 19. Configure application data volume directories
  - Configure directory creation for application data volumes
  - Set up proper permissions and ownership
  - _Requirements: 5.1, 6.1, 7.1_

- [ ] 20. Implement Excalidraw container configuration
  - Implement Excalidraw container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - _Requirements: 5.2, 6.2_

- [ ] 21. Configure Excalidraw GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:excalidraw
  - Set up container networking and dependencies
  - _Requirements: 5.2, 6.2_

- [ ] 22. Add certificate volume mounts for Excalidraw
  - Set up certificate volume mounts for excalidraw-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 5.2, 6.2_

- [ ] 23. Configure Excalidraw port mapping and Traefik labels
  - Configure port mapping and Traefik labels for service discovery
  - Set up routing rules and service configuration
  - _Requirements: 5.2, 6.2_

- [ ] 24. Implement Memos container configuration
  - Implement Memos container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - _Requirements: 5.3, 6.3_

- [ ] 25. Configure Memos GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:memos
  - Set up container networking and dependencies
  - _Requirements: 5.3, 6.3_

- [ ] 26. Add certificate volume mounts for Memos
  - Set up certificate volume mounts for memos-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 5.3, 6.3_

- [ ] 27. Configure Memos data persistence
  - Configure data persistence volume for /var/opt/memos
  - Set up proper volume mounting and permissions
  - _Requirements: 5.3, 6.3_

- [ ] 28. Implement Maybe Finance container configuration
  - Implement Maybe Finance container configuration in apps_services.compose.j2
  - Configure basic container settings and environment variables
  - _Requirements: 7.2, 7.3_

- [ ] 29. Configure Maybe Finance GhostTunnel sidecar
  - Configure GhostTunnel sidecar with network_mode: service:maybe-finance
  - Set up container networking and dependencies
  - _Requirements: 7.2, 7.3_

- [ ] 30. Add certificate volume mounts for Maybe Finance
  - Set up certificate volume mounts for maybe-finance-proxy certificates
  - Configure certificate file paths and permissions
  - _Requirements: 7.2, 7.3_

- [ ] 31. Configure Maybe Finance data persistence
  - Configure data persistence volume for /app/data
  - Set up proper volume mounting and permissions
  - _Requirements: 7.2, 7.3_

- [ ] 32. Create ztn_tcp_labels macro for TCP routing
  - Create ztn_tcp_labels macro for TCP routing with SNI
  - Implement macro logic for dynamic TCP service configuration
  - _Requirements: 8.1, 8.3_

- [ ] 33. Update Traefik dynamic configuration for TCP services
  - Update Traefik dynamic configuration for TCP services
  - Configure TCP routers and services for GhostTunnel
  - _Requirements: 8.1, 8.3_

- [ ] 34. Configure SSL passthrough for GhostTunnel services
  - Configure SSL passthrough for GhostTunnel services
  - Set up TLS configuration and SNI routing
  - _Requirements: 8.1, 8.3_

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
  - _Requirements: 8.4, 8.5_

- [ ] 39. Configure Traefik service discovery for application containers
  - Configure Traefik service discovery for application containers
  - Set up automatic service registration and routing
  - _Requirements: 8.4, 8.5_

- [ ] 40. Implement service removal logic for unavailable services
  - Implement service removal logic for unavailable services
  - Configure automatic cleanup of failed or stopped services
  - _Requirements: 8.4, 8.5_

- [ ] 41. Validate pki_services configuration mapping
  - Validate pki_services configuration mapping to service discovery
  - Implement configuration consistency checks
  - _Requirements: 9.1, 9.5_

- [ ] 42. Ensure DNS names and IP addresses are correctly mapped
  - Ensure DNS names and IP addresses are correctly mapped
  - Validate service discovery configuration consistency
  - _Requirements: 9.1, 9.5_

- [ ] 43. Implement configuration validation tasks
  - Implement configuration validation tasks
  - Add automated checks for configuration consistency
  - _Requirements: 9.1, 9.5_

- [ ] 44. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.