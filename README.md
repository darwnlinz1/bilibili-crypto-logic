# Bilibili.tv — Client-Side Auth Crypto (Reverse Engineered)

A standalone Python module that reproduces the RSA payload-encryption logic used
in the Bilibili.tv login flow. The project is a **security research exercise**:
it documents how the client protects credentials before transmission and
evaluates the design against modern cryptographic best practices.

> Full technical breakdown: see [`SECURITY_ANALYSIS.md`](./SECURITY_ANALYSIS.md).

## Mechanism

1. The client retrieves a dynamic `hash` string from the API.
2. The authentication payload is built by concatenating the hash and the raw
   password: `payload = hash + password`.
3. The payload is encrypted with a **hardcoded RSA-1024 public key** using
   **PKCS#1 v1.5** padding.
4. The ciphertext is Base64-encoded and sent to the authentication endpoint.

> This Python port replaces the original client's manual ASN.1/DER byte parsing
> with the standard `cryptography` library.

## Requirements

- Python 3.8+
- [`cryptography`](https://pypi.org/project/cryptography/)

## Installation

```bash
git clone https://github.com/darwnlinz1/bilibili-crypto-logic.git
cd bilibili-crypto-logic
pip install -r requirements.txt
```

## Usage

```python
from bilibili_crypto import encrypt_auth_payload, BILIBILI_PUB_KEY

login_hash = "dynamic_hash_from_api"
raw_password = "user_password"

encrypted_payload = encrypt_auth_payload(BILIBILI_PUB_KEY, login_hash, raw_password)
print(encrypted_payload)
```

## Security Notes

The scheme uses weak parameters by today's standards (RSA-1024, PKCS#1 v1.5
padding) and places the raw password inside the encrypted payload. Recommended
fixes — ≥2048-bit keys, RSA-OAEP, authenticated encryption, replay protection,
and never handling a raw password server-side — are detailed in
[`SECURITY_ANALYSIS.md`](./SECURITY_ANALYSIS.md).

## Disclaimer

This project is intended for **educational and security research purposes only**.
It contains no exploit code and no real credentials. The author is not
responsible for any misuse of this code.
