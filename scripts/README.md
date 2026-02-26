# Utility Scripts

This directory contains utility scripts for the homelab infrastructure automation project.

## Scripts

### `generate_service_password_hash.py`

Generates bcrypt password hashes for services that require hashed credentials (AdGuard Home, Traefik dashboard, etc.).

**Requirements:**

```bash
pip3 install bcrypt
```

**Usage:**

```bash
# Generate hash for a password (interactive output with Ansible vault instructions)
python3 scripts/generate_service_password_hash.py "your_password"

# Generate hash with custom cost factor
python3 scripts/generate_service_password_hash.py "your_password" --rounds 14

# Generate and verify the hash
python3 scripts/generate_service_password_hash.py "your_password" --verify

# Output only the hash (for piping / scripting)
python3 scripts/generate_service_password_hash.py "your_password" --quiet
```

**Output:**

- Bcrypt hash with configurable cost factor (default: 12 rounds)
- Ansible vault usage instructions showing which files to update
- Optional hash verification (`--verify`)
- Quiet mode for scripting (`--quiet`)

## Best Practices

- All utility scripts should be placed in this directory
- Scripts should be executable (`chmod +x script_name`)
- Include proper documentation and usage examples
- Use descriptive names following `snake_case` convention
- Include error handling and input validation