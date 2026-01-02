# Technology Stack

## Core Technologies

- **Ansible**: Infrastructure automation and configuration management
- **Docker**: Container runtime with Docker Compose for service orchestration  
- **Firewalld**: Linux firewall management
- **Traefik**: Cloud-native reverse proxy with automatic service discovery
- **AdGuard Home**: DNS server with ad-blocking capabilities

## Dependencies & Collections

### Ansible Collections
- `ansible.posix` (>=2.1.0) - POSIX system modules
- `community.crypto` (>=3.0.5) - PKI and certificate management
- `community.general` (>=12.1.0) - General purpose modules
- `community.docker` (>=5.0.4) - Docker container management
- `geerlingguy.docker` (>=7.9.0) - Docker installation role

### System Requirements
- Python 3 with `python3-docker` SDK
- SSH access with ED25519 key pairs
- Sudo privileges for target hosts

## Common Commands

### Initial Setup
```bash
# Install Ansible collections and external roles
ansible-galaxy install -r requirements.yml -p galaxy_roles/
ansible-galaxy collection install -r requirements.yml

# Run full playbook
ansible-playbook site.yml

# Run specific tags
ansible-playbook site.yml --tags "common,security"
ansible-playbook site.yml --tags "pki,certificates"
ansible-playbook site.yml --tags "network,firewall" --limit Gateways
ansible-playbook site.yml --tags "docker,traefik" --limit Gateways
```

### Development & Testing
```bash
# Check syntax
ansible-playbook site.yml --syntax-check

# Dry run
ansible-playbook site.yml --check

# Run on specific host
ansible-playbook site.yml --limit bastion_automation

# Skip specific tags
ansible-playbook site.yml --skip-tags "docker"
```

### Certificate Management
```bash
# Regenerate PKI certificates
ansible-playbook site.yml --tags "pki" --extra-vars "force_cert_regen=true"

# Deploy certificates only
ansible-playbook site.yml --tags "deploy-certs"
```

## Configuration Files

- `ansible.cfg`: Ansible behavior and performance settings
- `inventory.ini`: Host groups and target systems
- `site.yml`: Main playbook orchestrating all roles
- `group_vars/`: Group-specific variables and configuration
- `.pki_output/`: Generated certificates and keys (local)
- `.ssh_keys/`: Generated SSH key pairs (local)