# Security Analysis — Bilibili.tv Client-Side Authentication

**Document type:** Security research write-up
**Author:** darwnlinz1
**Status:** Public, sensitive material redacted

## 1. Executive Summary

This research analyzes how the Bilibili.tv client protects login credentials
before sending them to the server. The client concatenates a dynamic `hash`
string retrieved from the API with the raw password, then encrypts the whole
string with **RSA-1024 and PKCS#1 v1.5 padding**, using a **hardcoded public key
embedded in the client**, and finally Base64-encodes and transmits it. The design
uses the RSA concept correctly but chooses outdated parameters and payload format
(1024-bit key, legacy padding, raw password inside the payload). This report
documents the analysis method, assesses the risk, and proposes fixes based on
modern best practices.

## 2. Scope & Ethics

- All analysis was performed on software/services I **accessed legally with my
  own account**, for educational and security-research purposes.
- **No systems were attacked.** No unauthorized access was made, and no servers or
  other people's accounts were targeted.
- This report contains **no exploit code and no real credentials**. The public key
  already ships inside the client and is not a secret; all passwords/hashes shown
  are dummy data.
- Goal: demonstrate the ability to analyze a closed authentication flow and
  propose improvements.

## 3. Methodology

- **Environment:** a personal, isolated machine.
- **Approach:**
  1. Identify the steps the client performs during login (fetch dynamic hash →
     build payload → encrypt → send).
  2. Determine the algorithm, key size, and padding type.
  3. Independently reproduce the flow with a Python module (`cryptography`),
     replacing the original client's manual ASN.1/DER byte parsing with the
     standard library.
- **Definition of "understood correctly":** reconstruct the exact payload format
  (`hash + password`) and produce a valid ciphertext with the public key, without
  reusing the original binary.

## 4. Technical Findings

**Algorithm:** RSA-1024 with **PKCS#1 v1.5** padding.

**Payload construction:**

1. The client retrieves a **dynamic** `hash` string from the API.
2. It concatenates directly: `payload = hash + password` (password in **raw**
   form).
3. The payload is encrypted with a **hardcoded RSA-1024 public key** embedded in
   the client.
4. The ciphertext is Base64-encoded and sent to the authentication endpoint.

**Data flow:**

```
[API returns a dynamic hash]
        │
        ▼
[payload = hash + raw password]
        │
        ▼
[RSA-1024 encryption / PKCS#1 v1.5 with the hardcoded public key]
        │
        ▼
[Base64 encoding] ──► sent to the login endpoint
```

**Key handling:** an RSA-1024 public key is embedded in the client (it is public
by nature, not a secret). RSA uses no IV. No additional integrity/authentication
layer was found.

## 5. Security Assessment

- **RSA-1024 is too weak by today's standards.** Modern guidance recommends at
  least **2048 bits**; 1024-bit is considered obsolete.
- **PKCS#1 v1.5 padding is outdated.** It has a history of *padding oracle*
  vulnerabilities (Bleichenbacher); the modern standard is **RSA-OAEP**.
- **The raw password sits inside the payload.** Placing an unhashed password in the
  encrypted blob means that after decryption the server sees the raw password —
  increasing risk if the server is compromised or logs incorrectly.
- **The dynamic `hash` may be a replay defense, but is not sufficient alone.**
  Without strict time/nonce binding and integrity, its value is limited.
- **RSA alone lacks integrity.** Encryption on its own does not prove the data was
  not modified.
- **Context note:** the transport channel is usually already protected by TLS. The
  client-side RSA layer is defense-in-depth; with weak parameters it mostly
  creates a feeling of safety rather than real safety (*security theater*).

## 6. Recommendations

If this were my own system, I would:

1. **Upgrade to RSA keys ≥ 2048 bits** (or move to modern elliptic-curve key
   exchange).
2. **Replace PKCS#1 v1.5 with RSA-OAEP (SHA-256).**
3. **Never put the raw password in the payload.** Authenticate with a standard
   protocol (server-side hashing with Argon2/bcrypt, or a scheme like SRP) so the
   server never sees the raw password.
4. **Use authenticated hybrid encryption:** AES-256-GCM for the data plus RSA-OAEP
   to wrap the key, ensuring both confidentiality and integrity.
5. **Bind the dynamic `hash` to a nonce and an expiry** to defend against replay
   attacks.
6. **Rely on TLS as the primary transport-security layer**, treating client-side
   encryption as an addition rather than a replacement.

## 7. Conclusion & What I Learned

This exercise built skills in reading and reproducing a closed authentication
flow, recognizing why RSA-1024 + PKCS#1 v1.5 + a raw password are risky choices,
and understanding the role of nonces / dynamic hashes in replay protection. The
biggest takeaway: using the right algorithm is not enough — the **parameters and
payload format** are what determine whether a system is truly secure or merely
looks secure.

> *Disclaimer: This document is for educational and security-research purposes
> only. It contains no exploit code and no real credentials.*
