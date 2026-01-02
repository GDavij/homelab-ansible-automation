# Project Structure

## Directory Organization

### Root Level
- `site.yml` - Main playbook entry point orchestrating all roles
- `ansible.cfg` - Ansible configuration with performance optimizations
- `inventory.ini` - Host inventory defining Gateways, Workstations, Controllers
- `requirements.yml` - Ansible collections and role dependencies

### Configuration Management
```
group_vars/
├── all.yml                    # Global variables (PKI, SSH, Docker config)
└── Gateways/
    ├── networking.yml         # Network-specific variables
    ├── users.yml             # User management for gateway hosts
    └── adguard.yml           # AdGuard Home configuration variables
```

### Role Architecture
```
roles/                       # Custom project roles
├── common/                  # Base system setup (locale, packages)
├── security/                # SSH hardening, user management, key deployment
├── network_gateways/        # Firewall policies, interface trust, UFW removal
├── pki/                     # Certificate Authority and service certificate generation
├── docker/                  # Docker installation wrapper (uses geerlingguy.docker)
└── infra_gateways/          # Infrastructure services (Traefik, AdGuard, etc.)

galaxy_roles/                # External roles from Ansible Galaxy
└── geerlingguy.docker/      # Community Docker installation role
```

### Generated Assets (Local)
```
.pki_output/                 # Generated CA and service certificates
.ssh_keys/                   # Generated SSH key pairs per host
├── bastion/
│   ├── gatekeeper_id_ed25519
│   └── vanguard_id_ed25519
```

### Collections
```
collections/ansible_collections/
├── ansible/posix/           # POSIX system modules
├── community/crypto/        # PKI and certificate management
├── community/general/       # General purpose modules
└── community/docker/        # Docker container management
```

## Role Conventions

### External Role Management
- External roles (from Ansible Galaxy) should be installed separately from custom roles
- Use `ansible-galaxy install -r requirements.yml -p galaxy_roles/` to install to a dedicated directory
- Update `ansible.cfg` to include both paths: `roles_path = ./roles:./galaxy_roles`
- Never commit external roles to version control - use `requirements.yml` instead

### Task Organization
- `main.yml` - Primary task orchestration with includes
- Separate task files for logical groupings (e.g., `setup_culture.yml`, `firewall-policies.yml`)
- Use `include_tasks` for conditional logic, `import_tasks` for static includes

### Template Structure
- Jinja2 templates in `templates/` directory
- Docker Compose files use `.j2` extension
- Configuration files follow service naming (e.g., `traefik-dynamic.yml.j2`)

### Variable Hierarchy
1. `group_vars/all.yml` - Global defaults
2. `group_vars/[GroupName]/` - Group-specific overrides
3. Role defaults in `defaults/main.yml`
4. Role variables in `vars/main.yml`

## Naming Conventions

### Hosts & Groups
- **Gateways**: Network edge nodes (bastion_automation)
- **Workstations**: End-user systems (monster)
- **Controllers**: Management nodes (ghost)
- **Homelab**: All managed infrastructure

### Services & DNS
- Internal domain: `.lab` (e.g., `dns.lab`, `gateway.lab`)
- Service naming: descriptive lowercase (adguard, traefik)
- Certificate naming: matches service name

### Files & Directories
- Snake_case for role names and task files
- Kebab-case for configuration templates
- ED25519 key format: `{username}_id_ed25519`