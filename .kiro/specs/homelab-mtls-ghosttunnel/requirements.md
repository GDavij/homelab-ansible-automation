# Requirements Document

## Introduction

This specification defines the implementation of homelab applications secured with mutual TLS (mTLS) authentication using GhostTunnel as a proxy layer. The system will deploy containerized applications (Upsnap, Excalidraw, Memos, Maybe Finance) behind GhostTunnel proxies that enforce client certificate authentication, providing enterprise-grade security for internal homelab services.

## Glossary

- **GhostTunnel**: A simple TLS proxy with mutual authentication support for securing connections
- **mTLS**: Mutual Transport Layer Security - bidirectional authentication where both client and server verify each other's certificates
- **Homelab_System**: The Ansible-managed infrastructure automation system for homelab environments
- **Application_Container**: Docker containers running the target applications (Upsnap, Excalidraw, Memos, Maybe Finance)
- **PKI_Infrastructure**: The existing Public Key Infrastructure for certificate generation and management
- **Service_Discovery**: Traefik-based reverse proxy system for routing and load balancing
- **Client_Certificate**: X.509 certificates issued to clients for mTLS authentication
- **pki_services**: Variable list defining services requiring server certificates with DNS names, descriptions, and IP addresses
- **pki_client_devices**: Variable list defining client devices requiring client certificates with common names, descriptions, and user assignments

## Requirements

### Requirement 1

**User Story:** As a homelab administrator, I want to deploy GhostTunnel proxies for each application, so that all network traffic is secured with mutual TLS authentication.

#### Acceptance Criteria

1. WHEN the system deploys an application container, THE Homelab_System SHALL create a corresponding GhostTunnel proxy container
2. WHEN a GhostTunnel proxy starts, THE Homelab_System SHALL configure it with server certificates from the PKI_Infrastructure
3. WHEN a GhostTunnel proxy receives a connection, THE GhostTunnel SHALL require valid client certificates for authentication
4. WHEN client certificate validation fails, THE GhostTunnel SHALL reject the connection and log the authentication failure
5. WHEN client certificate validation succeeds, THE GhostTunnel SHALL forward the connection to the backend Application_Container

### Requirement 2

**User Story:** As a homelab administrator, I want to integrate GhostTunnel with the existing PKI infrastructure, so that certificate management is automated and consistent.

#### Acceptance Criteria

1. WHEN extending pki_services configuration, THE PKI_Infrastructure SHALL generate server certificates for each service defined in the pki_services variable list
2. WHEN generating server certificates, THE PKI_Infrastructure SHALL include DNS names and IP addresses from the pki_services configuration as Subject Alternative Names
3. WHEN generating client certificates, THE PKI_Infrastructure SHALL use the existing pki_client_devices configuration without modification
4. WHEN certificates are near expiration, THE Homelab_System SHALL regenerate and deploy new certificates automatically
5. WHEN certificate deployment occurs, THE Homelab_System SHALL restart affected GhostTunnel containers to load new certificates
6. WHEN certificate validation occurs, THE GhostTunnel SHALL verify certificates against the configured Certificate Authority

### Requirement 3

**User Story:** As a homelab administrator, I want to deploy Upsnap application with mTLS security, so that Wake-on-LAN functionality is protected from unauthorized access.

#### Acceptance Criteria

1. WHEN deploying Upsnap, THE Homelab_System SHALL create an Upsnap Application_Container listening on localhost
2. WHEN configuring Upsnap proxy, THE Homelab_System SHALL deploy a GhostTunnel container forwarding to the Upsnap container
3. WHEN Upsnap GhostTunnel starts, THE GhostTunnel SHALL bind to the configured port with mTLS enabled
4. WHEN external clients connect to Upsnap, THE GhostTunnel SHALL enforce client certificate authentication
5. WHEN authentication succeeds, THE GhostTunnel SHALL proxy requests to the backend Upsnap container

### Requirement 3.1

**User Story:** As a homelab administrator, I want Upsnap to be automatically configured with homelab machines, so that Wake-on-LAN functionality is ready to use without manual configuration.

#### Acceptance Criteria

1. WHEN deploying Upsnap, THE Homelab_System SHALL automatically configure Upsnap with machines defined in upsnap_machines variable list
2. WHEN upsnap_machines configuration is provided, THE Homelab_System SHALL generate Upsnap configuration files with machine names, IP addresses, and MAC addresses
3. WHEN SSH keys are specified for machines, THE Homelab_System SHALL configure Upsnap with the appropriate SSH key paths for remote power management
4. WHEN Upsnap starts, THE Upsnap SHALL be pre-configured with all homelab machines and ready for Wake-on-LAN operations
5. WHEN machine configurations change, THE Homelab_System SHALL update Upsnap configuration and restart the service

### Requirement 4

**User Story:** As a homelab administrator, I want to deploy Upsnap application with mTLS security, so that Wake-on-LAN functionality is protected from unauthorized access.

#### Acceptance Criteria

1. WHEN deploying Upsnap, THE Homelab_System SHALL create an Upsnap Application_Container listening on localhost
2. WHEN configuring Upsnap proxy, THE Homelab_System SHALL deploy a GhostTunnel container forwarding to the Upsnap container
3. WHEN Upsnap GhostTunnel starts, THE GhostTunnel SHALL bind to the configured port with mTLS enabled
4. WHEN external clients connect to Upsnap, THE GhostTunnel SHALL enforce client certificate authentication
5. WHEN authentication succeeds, THE GhostTunnel SHALL proxy requests to the backend Upsnap container

### Requirement 5

**User Story:** As a homelab administrator, I want to deploy Excalidraw application with mTLS security, so that collaborative drawing sessions are protected from unauthorized access.

#### Acceptance Criteria

1. WHEN deploying Excalidraw, THE Homelab_System SHALL create an Excalidraw Application_Container listening on localhost
2. WHEN configuring Excalidraw proxy, THE Homelab_System SHALL deploy a GhostTunnel container forwarding to the Excalidraw container
3. WHEN Excalidraw GhostTunnel starts, THE GhostTunnel SHALL bind to the configured port with mTLS enabled
4. WHEN external clients connect to Excalidraw, THE GhostTunnel SHALL enforce client certificate authentication
5. WHEN authentication succeeds, THE GhostTunnel SHALL proxy requests to the backend Excalidraw container

### Requirement 6

**User Story:** As a homelab administrator, I want to deploy Memos application with mTLS security, so that personal note-taking functionality is protected from unauthorized access.

#### Acceptance Criteria

1. WHEN deploying Memos, THE Homelab_System SHALL create a Memos Application_Container listening on localhost
2. WHEN configuring Memos proxy, THE Homelab_System SHALL deploy a GhostTunnel container forwarding to the Memos container
3. WHEN Memos GhostTunnel starts, THE GhostTunnel SHALL bind to the configured port with mTLS enabled
4. WHEN external clients connect to Memos, THE GhostTunnel SHALL enforce client certificate authentication
5. WHEN authentication succeeds, THE GhostTunnel SHALL proxy requests to the backend Memos container

### Requirement 7

**User Story:** As a homelab administrator, I want to deploy Maybe Finance application with mTLS security, so that financial data and budgeting functionality is protected from unauthorized access.

#### Acceptance Criteria

1. WHEN deploying Maybe Finance, THE Homelab_System SHALL create a Maybe Finance Application_Container listening on localhost
2. WHEN configuring Maybe Finance proxy, THE Homelab_System SHALL deploy a GhostTunnel container forwarding to the Maybe Finance container
3. WHEN Maybe Finance GhostTunnel starts, THE GhostTunnel SHALL bind to the configured port with mTLS enabled
4. WHEN external clients connect to Maybe Finance, THE GhostTunnel SHALL enforce client certificate authentication
5. WHEN authentication succeeds, THE GhostTunnel SHALL proxy requests to the backend Maybe Finance container

### Requirement 8

**User Story:** As a homelab administrator, I want to integrate GhostTunnel services with Traefik service discovery, so that applications remain accessible through the existing reverse proxy infrastructure.

#### Acceptance Criteria

1. WHEN GhostTunnel containers start, THE Homelab_System SHALL configure them with appropriate Docker labels for Service_Discovery
2. WHEN Traefik discovers GhostTunnel services, THE Service_Discovery SHALL route traffic to GhostTunnel proxy endpoints
3. WHEN configuring Traefik routes, THE Homelab_System SHALL preserve SSL passthrough to allow GhostTunnel to handle TLS termination
4. WHEN health checks occur, THE Service_Discovery SHALL verify GhostTunnel proxy availability
5. WHEN GhostTunnel services become unavailable, THE Service_Discovery SHALL remove them from routing tables

### Requirement 9

**User Story:** As a homelab administrator, I want to extend the existing all.yml configuration with GhostTunnel-specific variables, so that certificate generation and service configuration follows the established patterns.

#### Acceptance Criteria

1. WHEN configuring GhostTunnel services, THE Homelab_System SHALL extend the existing pki_services variable list with GhostTunnel proxy definitions
2. WHEN adding client authentication, THE Homelab_System SHALL utilize the existing pki_client_devices variable list without modification
3. WHEN GhostTunnel containers start, THE Homelab_System SHALL reference service configurations from the pki_services variable definitions
4. WHEN client certificates are deployed, THE Homelab_System SHALL use the existing pki_client_devices configuration for certificate distribution
5. WHEN service discovery occurs, THE Homelab_System SHALL map GhostTunnel services to their corresponding pki_services DNS names and IP addresses