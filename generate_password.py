#!/usr/bin/env python3
"""
Utility script to generate password hashes for admin authentication
"""

from werkzeug.security import generate_password_hash
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_password.py <password>")
        print("Example: python generate_password.py mypassword123")
        sys.exit(1)
    
    password = sys.argv[1]
    password_hash = generate_password_hash(password)
    
    print(f"Password: {password}")
    print(f"Hash: {password_hash}")
    print("\nAdd this to your .env file:")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")

if __name__ == '__main__':
    main()
