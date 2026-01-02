# Product Overview

## Homelab Infrastructure Automation

This is an Ansible-based infrastructure automation project designed to provision and manage a homelab environment. The system automates the deployment of gateway nodes, workstations, and controllers with a focus on security, networking, and containerized services.

### Key Features

- **Multi-tier Architecture**: Supports Gateways, Workstations, and Controllers with role-based configuration
- **Cloud-Native Reverse Proxy**: Traefik for modern load balancing and service discovery
- **PKI Management**: Automated certificate generation and deployment for internal services
- **Container Orchestration**: Docker-based service deployment with automatic service discovery
- **Security Hardening**: SSH key management, firewall configuration, and user access control
- **Service Discovery**: Internal DNS with AdGuard Home for local domain resolution

### Target Environment

Brazilian homelab setup (`.lab` domain) with services running on `192.168.1.0/24` subnet. Designed for self-hosted applications including DNS, proxy management, finance tracking, and productivity tools.

### Infrastructure Services

Core services include AdGuard DNS, Traefik reverse proxy, UpSnap (WoL), Excalidraw, Memos, and Maybe Finance - all accessible via internal PKI certificates and automatic service discovery.