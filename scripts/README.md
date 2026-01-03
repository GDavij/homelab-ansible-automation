# Utility Scripts

This directory contains utility scripts for the homelab infrastructure automation project.

## Scripts

### `generate_adguard_password.py`
Generates bcrypt password hashes for AdGuard Home authentication.

**Usage:**
```bash
# Generate hash for default password "changeme"
python3 scripts/generate_adguard_password.py

# Generate hash for custom password
python3 scripts/generate_adguard_password.py "your_password"
```

**Requirements:**
```bash
pip3 install bcrypt
```

**Output:**
- Displays bcrypt hashes with different rounds (10, 12)
- Provides verification of hash correctness
- Shows Ansible configuration format for copy/paste

## Best Practices

- All utility scripts should be placed in this directory
- Scripts should be executable (`chmod +x script_name`)
- Include proper documentation and usage examples
- Use descriptive names following snake_case convention
- Include error handling and input validation