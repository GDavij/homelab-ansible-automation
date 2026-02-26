# Changelog

All notable features and changes to the Homelab Ansible Automation project are documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] - 2026-02-22

### Current Release

The initial production-grade release of the homelab infrastructure automation, covering a 3-host topology (Controller, Gateway, Workstation) with full PKI, containerized services, and a GPU-accelerated Kubernetes cluster.

### Infrastructure

- Automated provisioning of a bastion gateway (Debian) and GPU workstation (Fedora 42) via SSH
- Bootstrap playbook for user creation, SSH hardening, and sudo configuration
- Sequenced playbook execution: bootstrap, certificates, gateways, workstations
- Unified `site.playbook.yml` for full-stack deployment in a single run
- Idempotent design across all playbooks — safe to re-run at any time

### PKI & Security

- Local Certificate Authority with root CA, intermediate, and service-level certificates
- mTLS enforcement on all gateway services via Ghostunnel sidecars
- Ansible Vault encryption for all secrets (database credentials, password hashes, certificate passphrases)
- Strict private key permissions (0600) across all certificate deployments
- Bastion pattern — workstation firewall only accepts SSH from the gateway IP

### Gateway Services (Docker Compose)

- Traefik reverse proxy with mTLS termination and dynamic routing
- AdGuard Home DNS server with ad blocking and custom rewrites
- Upsnap Wake-on-LAN management interface
- Memos daily journal application
- Sure Finance personal finance tracker (PostgreSQL + Redis backend)
- Trilium Notes personal knowledge base
- Post-deployment health verification for all Docker Compose stacks
- Container image versions extracted into `group_vars/Gateways/versions.yml` for centralized management

### Kubernetes Cluster (Single-Node)

- Kubeadm-based cluster initialization with configurable version (`kubernetes_version` variable)
- Block/rescue pattern on cluster init with automatic kubelet log collection on failure
- Kubernetes reset gated behind `k8s_force_reset` variable to prevent accidental cluster destruction
- RBAC governance policies applied at cluster bootstrap
- Kubeconfig distribution to controller and workstation users

### Kubernetes Platform Services

- Traefik Ingress controller with CRD installation and TLS configuration
- ArgoCD GitOps deployment with server-side apply and mTLS certificates
- Longhorn distributed block storage with SSD/HDD node configuration and CRD wait conditions
- Metrics Server for Horizontal Pod Autoscaler support with APIService readiness verification
- NVIDIA GPU device plugin with node labeling and runtime class configuration

### Kubernetes Module Adoption

- All `kubectl` command tasks migrated to `kubernetes.core.k8s` for native idempotency
- `kubernetes.core.k8s_info` for declarative wait conditions (CRD establishment, APIService availability)
- `kubernetes.core.k8s_taint` for control plane scheduling configuration
- Server-side apply support for ArgoCD HA manifest
- `kubernetes.core >= 6.3.0` collection dependency

### NVIDIA GPU Support

- NVIDIA driver installation for Fedora workstations
- Containerd runtime configuration for GPU passthrough
- Kubernetes GPU scheduling via device plugin DaemonSet and RuntimeClass

### Networking & Firewall

- Firewalld configuration on both gateway and workstation
- UFW removal on Debian gateways (replaced by firewalld)
- IP forwarding and masquerading for gateway routing
- Tailscale VPN integration (optional, gated behind `enable_tailscale`)
- Docker network CIDRs parameterized (`docker_core_net_cidr`, `docker_proxy_net_cidr`)

### Configuration Management

- Variable hierarchy: inventory → `group_vars/all.yml` → `group_vars/{Group}/` → `host_vars/{host}/`
- All hardcoded hostnames extracted into variables (`node_hostname`, `cluster_domain`, `cluster_endpoint`)
- Traefik version aligned across Docker Compose and Kubernetes deployments via `traefik_version` variable
- Subnet CIDR deduplicated into `group_vars/all.yml`

### Code Quality

- All task names and comments in English
- Role naming follows Ansible Lint convention (`snake_case`)
- Role-specific handler names to prevent cross-role handler conflicts
- `ansible.builtin.command` used instead of `shell` where no shell features are needed
- Proper `changed_when` and `failed_when` on all command tasks

### CI/CD & Tooling

- GitHub Actions workflow for automated ansible-lint validation on push and pull request
- `.ansible-lint` with production profile and curated skip/warn lists
- `.yamllint` with 160-character line limit and strict truthy values (`true`/`false` only)
- `meta/main.yml` for all 16 roles with platform targeting and dependency declarations

### Documentation

- Comprehensive README with Mermaid architecture diagram, network layout, and security model
- Setup guide with inventory template, vault configuration, and playbook execution order
- Recovery procedures for failed runs, certificate rotation, and cluster rebuilds
- Contributing guidelines with language, naming, and idempotency standards
