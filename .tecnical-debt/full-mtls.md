# 🏠 Homelab Ansible Automation

> **Mission**: Building a zero-trust, mTLS-everywhere homelab infrastructure with enterprise-grade security practices.

[![Ansible](https://img.shields.io/badge/Ansible-2.9%2B-EE0000?logo=ansible)](https://www.ansible.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![Security](https://img.shields.io/badge/Security-mTLS-green)](https://en.wikipedia.org/wiki/Mutual_authentication)
[![License](https://img.shields.io/badge/License-Personal-blue)]()

---

## 📋 Table of Contents

- [Overview](#overview)
- [Current Architecture](#current-architecture)
- [Security Model: The mTLS Journey](#security-model-the-mtls-journey)
- [Infrastructure Components](#infrastructure-components)
- [Quick Start](#quick-start)
- [Roadmap](#roadmap)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

This is a **security-first** Ansible automation project for managing a Brazilian homelab environment. The infrastructure consists of:

- **🛡️ Gateways (Bastions)**: Secure entry points with hardened SSH, mTLS-protected services, and network segmentation
- **💪 Workstations**: High-performance nodes with NVIDIA GPU support for AI/ML workloads
- **🎮 Controllers**: Local development machines orchestrating the infrastructure

### Key Features

✅ **Automated PKI Management**: Full certificate lifecycle with Root CA, intermediate CAs, and service certificates  
✅ **mTLS Authentication**: Mutual TLS for user-facing services using GhostTunnel sidecar pattern  
✅ **Zero Trust Networking**: Tailscale overlay + firewalld zones + SSH hardening  
✅ **GPU Automation**: NVIDIA driver installation and Docker GPU runtime for AI workloads  
✅ **Service Discovery**: Traefik reverse proxy with automatic service discovery  
✅ **Infrastructure as Code**: Fully reproducible, idempotent Ansible playbooks  

### Target Environment

- **Domain**: `.lab` (internal)
- **Subnet**: `192.168.1.0/24`
- **Timezone**: `America/Sao_Paulo`
- **OS Support**: Debian/Ubuntu and RHEL/Fedora families

---

## 🏗️ Current Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INTERNET / LAN                             │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                │ HTTPS (TLS)
                                ↓
                    ┌───────────────────────┐
                    │   Firewalld Zones     │
                    │  - underlay_network   │
                    │  - ztn_network        │
                    └───────────┬───────────┘
                                │
                                ↓
                    ┌───────────────────────┐
                    │   Traefik v3.6.6      │
                    │  - TLS termination    │
                    │  - Service routing    │
                    │  - Auto-discovery     │
                    └───────────┬───────────┘
                                │
                                │ HTTP (Docker network)
                                ↓
                    ┌───────────────────────┐
                    │  GhostTunnel Sidecar  │
                    │  - mTLS validation    │
                    │  - Client cert auth   │
                    │  - Port 8443          │
                    └───────────┬───────────┘
                                │
                                │ HTTP (localhost only)
                                ↓
                    ┌───────────────────────┐
                    │  Application Layer    │
                    │  - AdGuard Home       │
                    │  - Upsnap (WoL)       │
                    │  - Memos              │
                    │  - Sure Finance       │
                    │  - Trilium Notes      │
                    └───────────────────────┘
```

### Network Flow

1. **External Client** → Firewall (zone filtering)
2. **Firewall** → Traefik (TLS termination, routing)
3. **Traefik** → GhostTunnel (mTLS enforcement)
4. **GhostTunnel** → Application (localhost binding)

---

## 🔐 Security Model: The mTLS Journey

### Current State: mTLS at Service Layer ✅

**What We Have Today:**

| Component | Security Level | Status |
|-----------|---------------|--------|
| **User → Services** | mTLS (client certs required) | ✅ **IMPLEMENTED** |
| **SSH Access** | Key-based auth (ED25519) | ✅ **HARDENED** |
| **Firewall** | Zone-based segmentation | ✅ **ACTIVE** |
| **Application Isolation** | Localhost-only binding | ✅ **ENFORCED** |
| **PKI Infrastructure** | Automated CA + cert lifecycle | ✅ **OPERATIONAL** |

**Architecture Pattern:**
```yaml
services:
  application:
    image: app:latest
    network_mode: "service:ghosttunnel_sidecar"  # Share network stack
    
  ghosttunnel_sidecar:
    image: ghostunnel/ghostunnel:v1.8.4-alpine
    command:
      - server
      - --listen=0.0.0.0:8443
      - --target=127.0.0.1:8080
      - --cert=/etc/certs/server.crt
      - --key=/etc/certs/server.key
      - --cacert=/etc/certs/ca.crt
      - --allow-all  # Client cert validation
```

**Result:** Users must have valid client certificates to access services. No cert = no access.

---

### 🚧 The Gap: Full End-to-End mTLS

**What's NOT mTLS Yet:**

#### ❌ **Problem 1: Traefik → GhostTunnel Communication**

**Current Behavior:**
```yaml
# Traefik forwards to GhostTunnel without client cert
- traefik.http.services.adguard.loadbalancer.server.url=http://adguard:8443
```

**Issue:**
- Traefik doesn't present a client certificate to GhostTunnel
- Communication over Docker network is plain HTTP
- Relies on network isolation (acceptable but not zero-trust)

**Future Fix:**
```yaml
# Traefik needs to use HTTPS with client cert
- traefik.http.services.adguard.loadbalancer.server.scheme=https
- traefik.http.services.adguard.loadbalancer.serversTransport=mtls-transport@file

# Transport configuration
[http.serversTransports.mtls-transport]
  certificates:
    certFile = "/etc/traefik/client-certs/traefik.crt"
    keyFile = "/etc/traefik/client-certs/traefik.key"
  rootCAs = ["/etc/traefik/ca.crt"]
```

**Complexity:** Medium - Requires certificate management for Traefik itself

---

#### ❌ **Problem 2: Service-to-Service Communication**

**Current Behavior:**
```yaml
# Apps communicate over Docker networks without encryption
services:
  app_a:
    networks: [internal]
  app_b:
    networks: [internal]
```

**Issue:**
- If container escapes occur, attacker can sniff traffic
- No mutual authentication between services
- Trust boundary is at Docker network level

**Future Fix (Option A - K8s Service Mesh):**
```yaml
# Istio/Linkerd automatically injects mTLS sidecars
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT  # All pod-to-pod traffic requires mTLS
```

**Future Fix (Option B - Manual GhostTunnel Mesh):**
```yaml
# Each service needs both client and server GhostTunnel
services:
  app_a_server:
    image: ghostunnel/ghostunnel
    command: [server, --allow-cn=app_b.lab]
    
  app_a_client:
    image: ghostunnel/ghostunnel
    command: [client, --connect=app_b:8443]
```

**Complexity:** High - Exponential complexity without automation (K8s service mesh solves this)

---

#### ❌ **Problem 3: Database Connections**

**Current Behavior:**
```yaml
# PostgreSQL connections without TLS
environment:
  - DATABASE_URL=postgresql://user:pass@postgres:5432/db
```

**Issue:**
- Database credentials in environment variables
- No encryption for DB traffic
- Password-based auth (not certificate-based)

**Future Fix:**
```yaml
# PostgreSQL with certificate authentication
environment:
  - DATABASE_URL=postgresql://user@postgres:5432/db?sslmode=verify-full&sslcert=/certs/client.crt&sslkey=/certs/client.key&sslrootcert=/certs/ca.crt

# PostgreSQL server configuration
postgresql.conf:
  ssl = on
  ssl_cert_file = '/etc/certs/server.crt'
  ssl_key_file = '/etc/certs/server.key'
  ssl_ca_file = '/etc/certs/ca.crt'

pg_hba.conf:
  hostssl all all 0.0.0.0/0 cert  # Require client certificates
```

**Complexity:** Medium - Requires database-specific configuration

---

#### ❌ **Problem 4: Monitoring & Observability**

**Not Yet Implemented:**
- Prometheus scraping without mTLS
- Grafana dashboards without client certs
- Log shipping without encryption

**Future Fix:**
```yaml
# Prometheus with mTLS scraping
scrape_configs:
  - job_name: 'services'
    scheme: https
    tls_config:
      cert_file: /etc/prometheus/client.crt
      key_file: /etc/prometheus/client.key
      ca_file: /etc/prometheus/ca.crt
```

**Complexity:** Medium - Need to instrument all exporters

---

### 🎯 The Vision: mTLS Everywhere

**Target Architecture:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ZERO-TRUST ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  mTLS   ┌─────────────┐  mTLS   ┌─────────────┐  │
│  │   Client    │────────▶│   Traefik   │────────▶│ GhostTunnel │  │
│  │  (Browser)  │         │  (Gateway)  │         │  (Service)  │  │
│  └─────────────┘         └─────────────┘         └─────────────┘  │
│        ▲                        ▲                        ▲          │
│        │                        │                        │          │
│        └────────────────────────┴────────────────────────┘          │
│                   ALL require valid certificates                   │
│                   issued by Homelab Root CA                        │
│                                                                     │
│  ┌─────────────┐  mTLS   ┌─────────────┐  mTLS   ┌─────────────┐  │
│  │  Service A  │◀───────▶│  Service B  │◀───────▶│  Database   │  │
│  └─────────────┘         └─────────────┘         └─────────────┘  │
│                                                                     │
│  ┌─────────────┐  mTLS   ┌─────────────┐                          │
│  │ Prometheus  │────────▶│  Exporters  │                          │
│  └─────────────┘         └─────────────┘                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

PRINCIPLES:
✅ Never trust, always verify
✅ Every connection authenticated
✅ Every transmission encrypted
✅ Certificate rotation automated
✅ Least privilege access
```

---

### 📅 Roadmap to Full mTLS

#### **Phase 1: Foundation** ✅ **COMPLETED**
- [x] Automated PKI infrastructure
- [x] Root CA and intermediate CAs
- [x] Service certificate generation
- [x] Client certificate distribution
- [x] GhostTunnel sidecars for user services

#### **Phase 2: Kubernetes Migration** 🔄 **IN PROGRESS**
- [ ] K8s cluster setup (K3s or RKE2)
- [ ] Cert-manager integration with existing PKI
- [ ] Service mesh evaluation (Istio vs Linkerd)
- [ ] Automatic mTLS for pod-to-pod traffic
- [ ] Ingress controller with client cert validation

#### **Phase 3: Service Mesh** 🔮 **PLANNED**
- [ ] Deploy service mesh (Istio/Linkerd)
- [ ] Enable STRICT mTLS mode cluster-wide
- [ ] Certificate rotation automation
- [ ] mTLS observability (connection metrics)
- [ ] Policy enforcement (AuthorizationPolicy)

#### **Phase 4: Application Layer** 🔮 **PLANNED**
- [ ] Database mTLS (PostgreSQL, Redis)
- [ ] Message queue mTLS (RabbitMQ, Kafka)
- [ ] Cache layer mTLS
- [ ] Object storage mTLS (MinIO)

#### **Phase 5: Observability** 🔮 **PLANNED**
- [ ] Prometheus with mTLS scraping
- [ ] Grafana with client cert auth
- [ ] Loki log aggregation with mTLS
- [ ] Jaeger tracing with mTLS
- [ ] AlertManager with mTLS webhooks

#### **Phase 6: Full Zero-Trust** 🔮 **FUTURE**
- [ ] mTLS for SSH (certificate-based)
- [ ] Network policies blocking non-mTLS traffic
- [ ] Automated certificate expiry monitoring
- [ ] Certificate revocation automation
- [ ] Intrusion detection on cert validation failures

---

### 🤔 Why This Matters

**Traditional Security:**
```
Firewall → VPN → Application (password)
   ↑         ↑          ↑
  🔓       🔓        🔓
  │        │          │
  ├─ Once breached, full access
  ├─ Lateral movement easy
  └─ No per-service authentication
```

**mTLS Everywhere:**
```
mTLS → mTLS → mTLS → mTLS
 ↑      ↑      ↑      ↑
🔐    🔐    🔐    🔐
 │      │      │      │
 ├─ Every hop authenticated
 ├─ Lateral movement blocked
 └─ Certificate-based access control
```

**Result:** Even if an attacker compromises one service, they cannot access others without valid certificates.

---

## 🛠️ Infrastructure Components

### Gateway Services (Bastions)

| Service | Purpose | mTLS Status | Port |
|---------|---------|-------------|------|
| **Traefik** | Reverse proxy + LB | TLS only | 80, 443 |
| **AdGuard Home** | DNS + Ad blocking | ✅ mTLS | 8443 |
| **Upsnap** | Wake-on-LAN | ✅ mTLS | 8443 |
| **Memos** | Note-taking | ✅ mTLS | 8443 |
| **Sure Finance** | Financial tracking | ✅ mTLS | 8443 |
| **Trilium Notes** | Knowledge base | ✅ mTLS | 8443 |
| **Tailscale** | Zero-trust VPN | WireGuard | 41641 |

### Workstation Features

- **NVIDIA GPU Support**: Automated driver installation (Fedora/RHEL)
- **Docker GPU Runtime**: `nvidia-container-toolkit` for AI workloads
- **SSH Restrictions**: Only accessible from Gateway IPs
- **Power Management**: Tuned for always-on operation

### Security Features

| Feature | Implementation | Status |
|---------|---------------|--------|
| **SSH Hardening** | ED25519 keys, password auth disabled | ✅ Active |
| **User Management** | Automated user/group creation | ✅ Active |
| **Firewall Zones** | underlay_network, ztn_network | ✅ Active |
| **Egress Filtering** | Block SMB, SMTP, unwanted protocols | ✅ Active |
| **Certificate Validation** | Pre-deployment verification | ✅ Active |
| **Service Isolation** | Localhost-only application binding | ✅ Active |

---

## 🚀 Quick Start

### Prerequisites

- **Control Machine**:
  - Ansible 2.9+
  - Python 3.8+
  - SSH client with ED25519 support

- **Target Hosts**:
  - Debian 11+ or Fedora 38+
  - SSH access with sudo privileges
  - Minimum 2GB RAM, 20GB disk

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd homelab-ansible-automation
   ```

2. **Install dependencies:**
   ```bash
   # Install Ansible collections
   ansible-galaxy collection install -r requirements.yml
   
   # Install external roles
   ansible-galaxy install -r requirements.yml -p galaxy_roles/
   ```

3. **Configure inventory:**
   ```bash
   # Copy inventory template
   cp inventory.example.ini inventory.ini
   
   # Edit with your IPs and credentials
   vim inventory.ini
   ```

4. **Customize variables:**
   ```bash
   # Review and modify group variables
   vim group_vars/all.yml
   vim group_vars/Gateways/*.yml
   vim group_vars/Workstations/*.yml
   ```

5. **Run the playbook:**
   ```bash
   # Syntax check first
   ansible-playbook site.yml --syntax-check
   
   # Dry run to preview changes
   ansible-playbook site.yml --check
   
   # Full deployment
   ansible-playbook site.yml
   ```

### Post-Deployment

1. **Import client certificates to browser:**
   ```bash
   # PKCS#12 file for Firefox/Chrome
   .pki_output/clients/gatekeeper.p12
   
   # Default password: changeme
   ```

2. **Verify services:**
   ```bash
   # Check Traefik dashboard
   https://gateway.lab
   
   # Access AdGuard Home
   https://adguard.lab
   
   # Test mTLS (should prompt for certificate)
   curl --cert .pki_output/clients/gatekeeper.crt \
        --key .pki_output/clients/gatekeeper.key \
        --cacert .pki_output/authorities/root-ca.crt \
        https://adguard.lab
   ```

3. **SSH to workstations (via bastion):**
   ```bash
   # SSH keys are in .ssh_keys/
   ssh -i .ssh_keys/bastion_automation/gatekeeper_id_ed25519 \
       gatekeeper@bastion.lab
   ```

---

## 🗺️ Roadmap

### Current Focus: Kubernetes Migration

**Goal:** Replace Docker Compose with Kubernetes for better orchestration and native service mesh support.

**Planned Stack:**
- **Distribution**: K3s (lightweight, production-ready)
- **Ingress**: Traefik (reuse existing config)
- **Service Mesh**: Linkerd (simple, low overhead) or Istio (feature-rich)
- **Cert Management**: cert-manager (integrated with existing PKI)
- **Storage**: Longhorn (distributed block storage)

**Why K8s?**
- 🔐 Native service mesh for automatic pod-to-pod mTLS
- 🔄 Better certificate rotation and lifecycle management
- 📊 Advanced observability and monitoring
- 🎯 Policy-driven security (NetworkPolicy, AuthorizationPolicy)
- 🚀 Scalability for future AI/ML workloads

### Next Milestones

- [ ] **2024 Q2**: K8s cluster deployment with cert-manager
- [ ] **2024 Q3**: Service mesh with STRICT mTLS mode
- [ ] **2024 Q4**: Migrate all services to K8s with mTLS
- [ ] **2025 Q1**: Full observability stack with mTLS
- [ ] **2025 Q2**: Database and storage layer mTLS
- [ ] **2025 Q3**: Network policies enforcing mTLS-only traffic

---

## 📁 Project Structure

```
homelab-ansible-automation/
├── ansible.cfg                 # Ansible configuration
├── site.yml                    # Master playbook (orchestrator)
├── gateways.yml                # Gateway-specific playbook
├── workstations.yml            # Workstation-specific playbook
├── inventory.ini               # Host inventory (gitignored)
├── inventory.example.ini       # Template for inventory
├── requirements.yml            # Ansible dependencies
│
├── group_vars/                 # Variable hierarchy
│   ├── all.yml                 # Global variables
│   ├── Gateways/               # Gateway-specific vars
│   │   ├── adguard.yml
│   │   ├── networking.yml
│   │   ├── traefik.yml
│   │   ├── upsnap.yml
│   │   └── users.yml
│   └── Workstations/           # Workstation-specific vars
│       ├── networking.yml
│       └── users.yml
│
├── roles/                      # Custom Ansible roles
│   ├── common/                 # Base system configuration
│   ├── security/               # SSH hardening, users
│   ├── docker/                 # Docker installation
│   ├── nvidia-gpu/             # GPU driver automation
│   ├── pki/                    # Certificate management
│   ├── network_gateways/       # Gateway firewall
│   ├── network_workstations/   # Workstation firewall
│   ├── tailscale/              # Zero Trust VPN
│   ├── infra_gateways/         # Core services (DNS, Traefik)
│   └── apps_gateways/          # Applications
│
├── .pki_output/                # Generated certificates (gitignored)
│   ├── authorities/            # CA certificates
│   ├── certs/                  # Service certificates
│   └── clients/                # Client certificates
│
├── .ssh_keys/                  # Generated SSH keys (gitignored)
│   ├── bastion_automation/
│   └── monster_automation/
│
├── scripts/                    # Utility scripts
│   └── generate_password.sh
│
└── .kiro/                      # Project management
    ├── steering/               # Product vision & tech docs
    │   ├── product.md
    │   └── tech.md
    └── specs/                  # Feature specifications
        └── homelab-mtls-ghosttunnel/
```

---

## ⚙️ Configuration

### Essential Variables (group_vars/all.yml)

```yaml
# System Configuration
default_timezone: "America/Sao_Paulo"
default_locale: "pt_BR.UTF-8"

# PKI Configuration
pki_root_ca_common_name: "Homelab Root CA"
pki_root_ca_validity_days: 7300  # 20 years
pki_service_cert_validity_days: 730  # 2 years
pki_output_folder: "{{ playbook_dir }}/.pki_output/"

# SSH Configuration
ssh_keys_dir: "{{ playbook_dir }}/.ssh_keys/{{ inventory_hostname }}"
security_ssh_key_type: "ed25519"

# Docker Configuration
docker_users:
  - gatekeeper
  - vanguard
```

### Gateway-Specific (group_vars/Gateways/)

```yaml
# Traefik Configuration
traefik_domain: "gateway.lab"
traefik_dashboard_enabled: true
traefik_letsencrypt_enabled: false  # Using internal PKI

# AdGuard Configuration
adguard_dns_port: 53
adguard_web_port: 3000
adguard_username: "gatekeeper"

# Upsnap Configuration
upsnap_web_port: 8090
upsnap_bind_address: "127.0.0.1"
```

### Workstation-Specific (group_vars/Workstations/)

```yaml
# User Configuration
system_users:
  - username: gdavij
    groups: sudo,docker,ssl-cert
    state: present

# GPU Configuration (for NVIDIA hosts)
nvidia_driver_install: true
nvidia_container_toolkit: true
```

---

## 🐛 Troubleshooting

### SSH Connection Issues

**Problem:** Cannot connect after SSH hardening
```bash
# Solution: Use generated SSH keys
ssh -i .ssh_keys/bastion_automation/gatekeeper_id_ed25519 \
    gatekeeper@192.168.1.x
```

**Problem:** "Permission denied (publickey)"
```bash
# Verify key deployment
ansible-playbook site.yml --tags security --check

# Re-run security role
ansible-playbook site.yml --tags security
```

### Certificate Issues

**Problem:** Browser doesn't trust certificates
```bash
# Import Root CA to browser trust store
# Firefox: Settings → Certificates → Import
# File: .pki_output/authorities/root-ca.crt

# Import client certificate (PKCS#12)
# File: .pki_output/clients/gatekeeper.p12
# Password: changeme (default)
```

**Problem:** Certificate expired
```bash
# Regenerate certificates
ansible-playbook site.yml --tags pki \
  --extra-vars "force_cert_regen=true"
```

### Service Access Issues

**Problem:** "Client certificate required" error
```bash
# Ensure client cert is imported to browser
# Or use curl with certificate:
curl --cert .pki_output/clients/gatekeeper.crt \
     --key .pki_output/clients/gatekeeper.key \
     --cacert .pki_output/authorities/root-ca.crt \
     https://service.lab
```

**Problem:** Service not accessible
```bash
# Check Traefik routing
docker logs traefik

# Check GhostTunnel status
docker logs adguard_ghosttunnel

# Verify firewall rules
sudo firewall-cmd --list-all --zone=underlay_network
```

### Firewall Issues

**Problem:** Services blocked by firewall
```bash
# Check active zones
sudo firewall-cmd --get-active-zones

# List zone rules
sudo firewall-cmd --zone=underlay_network --list-all

# Temporarily add rule (testing)
sudo firewall-cmd --zone=underlay_network \
  --add-port=8443/tcp

# Reload firewall
sudo firewall-cmd --reload
```

### Docker Issues

**Problem:** Docker containers not starting
```bash
# Check Docker daemon
sudo systemctl status docker

# View container logs
docker compose -f /opt/homelab/infra_services.compose.yml logs

# Restart services
docker compose -f /opt/homelab/infra_services.compose.yml restart
```

### GPU Issues (Workstations)

**Problem:** nvidia-smi not found
```bash
# Verify driver installation
lsmod | grep nvidia

# Re-run nvidia-gpu role
ansible-playbook workstations.yml --tags nvidia-gpu

# Reboot may be required
sudo reboot
```

---

## 🤝 Contributing

This is a personal homelab project, but contributions and suggestions are welcome!

### Development Workflow

1. **Test changes on limited scope:**
   ```bash
   # Test on single host
   ansible-playbook site.yml --limit bastion_automation --check
   ```

2. **Use tags for targeted runs:**
   ```bash
   # Only run specific role
   ansible-playbook site.yml --tags pki
   ```

3. **Check syntax before committing:**
   ```bash
   ansible-playbook site.yml --syntax-check
   yamllint .
   ansible-lint site.yml
   ```

4. **Follow conventional commit format:**
   ```
   feat(#role-name): Add new feature
   fix(#role-name): Fix bug
   chore(#role-name): Maintenance
   docs(#role-name): Documentation
   ```

### Adding New Services

1. Define service in `group_vars/Gateways/<service>.yml`
2. Add GhostTunnel configuration to role template
3. Generate service certificate in `pki` role
4. Add firewall rules in `network_gateways` role
5. Add Traefik routing labels
6. Test mTLS access

---

## 📚 Additional Resources

### Documentation

- [Product Overview](.kiro/steering/product.md)
- [Technology Stack](.kiro/steering/tech.md)
- [mTLS GhostTunnel Spec](.kiro/specs/homelab-mtls-ghosttunnel/)

### External References

- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [GhostTunnel Documentation](https://github.com/ghostunnel/ghostunnel)
- [Traefik mTLS Guide](https://doc.traefik.io/traefik/https/tls/)
- [Zero Trust Architecture (NIST SP 800-207)](https://csrc.nist.gov/publications/detail/sp/800-207/final)

### Community

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Wiki**: For extended documentation

---

## 📜 License

Personal project - All rights reserved.

---

## 🙏 Acknowledgments

- **Ansible Community**: For incredible automation tools
- **GhostTunnel Team**: For making mTLS accessible
- **Traefik Labs**: For modern reverse proxy
- **Homelab Community**: For inspiration and knowledge sharing

---

## 📊 Project Status

**Current Phase:** Foundation Complete + K8s Migration Planning  
**mTLS Coverage:** ~40% (service layer only)  
**Target Coverage:** 100% (end-to-end zero-trust)  
**Estimated Completion:** 2025 Q3

---

<div align="center">

**Built with ❤️ for security, automation, and continuous learning**

*"Never trust, always verify. Encrypt everything, authenticate everyone."*

</div>
