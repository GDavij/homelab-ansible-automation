#!/usr/bin/env python3
"""
Service Password Hash Generator

Generates bcrypt password hashes for services that require hashed credentials.
Used by: AdGuard Home, Traefik dashboard, and any service needing bcrypt auth.

Usage:
    python3 scripts/generate_service_password_hash.py "your_password"
    python3 scripts/generate_service_password_hash.py "your_password" --rounds 14
    python3 scripts/generate_service_password_hash.py "your_password" --verify
"""

import argparse
import sys

try:
    import bcrypt
except ImportError:
    print("Error: bcrypt package is required.")
    print("Install it with: pip3 install bcrypt")
    sys.exit(1)


def generate_bcrypt_hash(password, rounds=12):
    """Generate bcrypt hash with specified rounds."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=rounds)
    hash_bytes = bcrypt.hashpw(password_bytes, salt)
    return hash_bytes.decode('utf-8')


def verify_hash(password, hash_string):
    """Verify password against an existing bcrypt hash."""
    password_bytes = password.encode('utf-8')
    hash_bytes = hash_string.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate bcrypt password hashes for Ansible vault service credentials.",
        epilog="Example: python3 %(prog)s 'my_secure_password'",
    )
    parser.add_argument(
        "password",
        nargs="?",
        default="changeme",
        help="Password to hash (default: 'changeme')",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=12,
        choices=range(4, 32),
        metavar="N",
        help="Bcrypt cost factor / number of rounds (default: 12)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run verification check against the generated hash",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Output only the hash (for piping to other commands)",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    password = args.password
    rounds = args.rounds

    password_hash = generate_bcrypt_hash(password, rounds=rounds)

    if args.quiet:
        print(password_hash)
        return

    print(f"Generating bcrypt hash (rounds={rounds}) for: '{password}'")
    print("=" * 60)
    print(f"Hash: {password_hash}")

    if args.verify:
        is_valid = verify_hash(password, password_hash)
        status = "Verification passed" if is_valid else "Verification FAILED"
        print(f"      {'✓' if is_valid else '✗'} {status}")

    print()
    print("=" * 60)
    print("ANSIBLE VAULT USAGE:")
    print("=" * 60)
    print("Paste the hash into the appropriate vault file:")
    print()
    print("  # group_vars/Gateways/adguard.vault.yml")
    print(f'  adguard_password_hash: "{password_hash}"')
    print()
    print("  # group_vars/Gateways/traefik.vault.yml")
    print(f'  traefik_dashboard_password_hash: "{password_hash}"')
    print()
    print("Then encrypt with: ansible-vault encrypt group_vars/Gateways/*.vault.yml")


if __name__ == "__main__":
    main()