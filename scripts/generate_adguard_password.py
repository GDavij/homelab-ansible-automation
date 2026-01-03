#!/usr/bin/env python3
"""
AdGuard Home Password Hash Generator
Generates bcrypt hash for AdGuard Home authentication
"""

import bcrypt
import sys

def generate_bcrypt_hash(password, rounds=12):
    """Generate bcrypt hash with specified rounds"""
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=rounds)
    hash_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Convert back to string
    return hash_bytes.decode('utf-8')

def verify_hash(password, hash_string):
    """Verify password against hash"""
    password_bytes = password.encode('utf-8')
    hash_bytes = hash_string.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

if __name__ == "__main__":
    # Default password
    password = "changeme"
    
    # Allow custom password via command line
    if len(sys.argv) > 1:
        password = sys.argv[1]
    
    print(f"Generating bcrypt hash for password: '{password}'")
    print("=" * 50)
    
    # Generate hash with different rounds for comparison
    for rounds in [10, 12]:
        hash_result = generate_bcrypt_hash(password, rounds)
        print(f"Rounds {rounds:2d}: {hash_result}")
        
        # Verify the hash works
        if verify_hash(password, hash_result):
            print(f"         ✓ Verification successful")
        else:
            print(f"         ✗ Verification failed")
        print()
    
    # Generate final hash for Ansible
    final_hash = generate_bcrypt_hash(password, rounds=12)
    
    print("=" * 50)
    print("ANSIBLE CONFIGURATION:")
    print("=" * 50)
    print(f'adguard_username: "gatekeeper"')
    print(f'adguard_password_hash: "{final_hash}"')
    print()
    print("Copy the hash above to your group_vars/Gateways/adguard.yml file")
    print(f"Login credentials: gatekeeper / {password}")