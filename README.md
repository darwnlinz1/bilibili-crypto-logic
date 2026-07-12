```markdown
# Bilibili TV Auth Crypto (Reverse Engineered)

A standalone Python module replicating the RSA payload encryption logic used in Bilibili.tv's authentication flow. 

## 🔍 Mechanism Analysis

1. The client retrieves a dynamic `hash` string.
2. The authentication payload is constructed by concatenating the hash and raw password: `payload = hash + password`.
3. The payload is encrypted using a hardcoded RSA-1024 public key with **PKCS#1 v1.5 padding**.
4. The ciphertext is Base64 encoded and transmitted to the API endpoint.

*Note: This Python port optimizes the original client's manual ASN.1/DER byte parsing by leveraging standard cryptography libraries.*

## 🚀 Installation & Usage

```bash
pip install cryptography

```

```python
from bilibili_crypto import encrypt_auth_payload, BILIBILI_PUB_KEY

login_hash = "dynamic_hash_from_api"
raw_password = "user_password"

encrypted_payload = encrypt_auth_payload(BILIBILI_PUB_KEY, login_hash, raw_password)
print(encrypted_payload)

```

## ⚠️ Disclaimer

```
This project is for educational and security research purposes only. The author is not responsible for any misuse of this code.
```
