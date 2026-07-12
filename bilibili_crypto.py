"""
Bilibili TV Authentication Crypto Module
Reverse-engineered RSA payload encryption logic for Bilibili.tv login flow.
"""

import base64
import logging
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Extracted hardcoded RSA Public Key from Bilibili.tv client
BILIBILI_PUB_KEY = (
    "-----BEGIN PUBLIC KEY-----\n"
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDjb4V7EidX/ym28t2ybo0U6t0n\n"
    "6p4ej8VjqKHg100va6jkNbNTrLQqMCQCAYtXMXXp2Fwkk6WR+12N9zknLjf+C9sx\n"
    "/+l48mjUU8RqahiFD1XT/u2e0m2EN029OhCgkHx3Fc/KlFSIbak93EH/XlYis0w+\n"
    "Xl69GV6klzgxW6d2xQIDAQAB\n"
    "-----END PUBLIC KEY-----"
)

def encrypt_auth_payload(pem_key: str, auth_hash: str, password: str) -> Optional[str]:
    """
    Encrypts the authentication payload using the target's specific RSA configuration.
    Payload construction: Hash + Raw Password
    Encryption standard: RSA-1024 with PKCS#1 v1.5 padding.
    """
    try:
        pub_key = serialization.load_pem_public_key(
            pem_key.encode('utf-8'),
            backend=default_backend()
        )

        plaintext_payload = f"{auth_hash}{password}".encode('utf-8')

        ciphertext = pub_key.encrypt(
            plaintext_payload,
            padding.PKCS1v15()
        )

        return base64.b64encode(ciphertext).decode('utf-8')
        
    except Exception as err:
        logging.error(f"Failed to encrypt authentication payload: {err}")
        return None

if __name__ == "__main__":
    logging.info("Initializing Bilibili reverse-engineered crypto module...")
    
    sample_api_hash = "d3b07384d113edec49eaa6238ad5ff00"
    sample_raw_password = "my_secure_password"
    
    encrypted_payload = encrypt_auth_payload(
        pem_key=BILIBILI_PUB_KEY, 
        auth_hash=sample_api_hash, 
        password=sample_raw_password
    )
    
    if encrypted_payload:
        logging.info(f"Encrypted (B64): {encrypted_payload}")
    else:
        logging.error("Encryption process failed.")