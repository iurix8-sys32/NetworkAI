#!/usr/bin/env python3
"""
Secure Token Storage with Encryption
Protects GitHub tokens with a PIN code
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

TOKEN_FILE = '/tmp/.gh_token.enc'
SALT_FILE = '/tmp/.gh_token.salt'
PIN_CODE = "251172"

def get_key(pin):
    """Derive encryption key from PIN"""
    if not os.path.exists(SALT_FILE):
        salt = os.urandom(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
    else:
        with open(SALT_FILE, 'rb') as f:
            salt = f.read()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(pin.encode()))
    return key

def encrypt_token(token, pin):
    """Encrypt a token with PIN"""
    f = Fernet(get_key(pin))
    encrypted = f.encrypt(token.encode())
    
    with open(TOKEN_FILE, 'wb') as f:
        f.write(encrypted)
    
    return True

def decrypt_token(pin):
    """Decrypt token with PIN"""
    if not os.path.exists(TOKEN_FILE):
        return None
    
    try:
        with open(TOKEN_FILE, 'rb') as f:
            encrypted = f.read()
        
        f = Fernet(get_key(pin))
        token = f.decrypt(encrypted).decode()
        return token
    except Exception:
        return None

def store_token(token):
    """Store token with default PIN"""
    return encrypt_token(token, PIN_CODE)

def get_token():
    """Get stored token with default PIN"""
    return decrypt_token(PIN_CODE)

def verify_pin(pin):
    """Verify if PIN is correct"""
    return pin == PIN_CODE

def is_token_stored():
    """Check if token exists"""
    return os.path.exists(TOKEN_FILE)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'store':
            if len(sys.argv) > 2:
                store_token(sys.argv[2])
                print("Token stored and encrypted")
            else:
                print("Usage: python token_storage.py store <token>")
        elif sys.argv[1] == 'get':
            token = get_token()
            if token:
                print(f"Token: {token[:10]}...")
            else:
                print("No token stored or invalid PIN")
        elif sys.argv[1] == 'verify':
            if len(sys.argv) > 2:
                if verify_pin(sys.argv[2]):
                    print("PIN verified!")
                else:
                    print("Invalid PIN")
        elif sys.argv[1] == 'init':
            # Initialize with provided token
            if len(sys.argv) > 2:
                store_token(sys.argv[2])
                print("Token initialized with PIN protection")
            else:
                print("Usage: python token_storage.py init <token>")
        else:
            print("Commands: store, get, verify, init")
    else:
        print("Token Storage System")
        print(f"  Stored: {is_token_stored()}")
        print(f"  PIN: {PIN_CODE}")