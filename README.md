# 🔐 RECTANGLE — Lightweight Block Cipher

A complete Python implementation of the **RECTANGLE** lightweight block cipher with an interactive Streamlit web application for encryption, decryption, and security analysis.

> Developed as part of the Internet of Things & Network Security (IoTNS) course  
> Lebanese University — Faculty of Engineering Branch I  
> Academic Year 2025–2026

---

## What is RECTANGLE?

RECTANGLE is a lightweight block cipher published in 2014, designed for constrained environments like IoT sensors and RFID tags. Its key innovation is a **bit-slice architecture**: the 64-bit state is arranged as a 4 × 16 grid, allowing all 16 columns to be processed simultaneously — making it fast in software and extremely cheap in hardware (~1600 gate equivalents).

| Property       | Value                          |
|----------------|--------------------------------|
| Block size     | 64 bits                        |
| Key sizes      | 80-bit or 128-bit              |
| Rounds         | 25                             |
| Structure      | SP-network (Sub–Perm)          |
| Hardware cost  | ~1600 GE, 3.0 pJ/bit           |
| Software speed | 30.5 cycles/byte (Intel Core i5)|

---

## Application Overview

The Streamlit app has **3 tabs** and an always-visible **sidebar**.

### Sidebar
Displays algorithm specs, a step-by-step usage guide, and all 4 official test vectors ready to copy-paste.

---

### Tab 1 — Encrypt / Decrypt

> Enter a 64-bit plaintext and key in hex, choose a mode, and run.

![Encrypt/Decrypt Tab](tab1_encrypt.png)

- Supports both 80-bit and 128-bit keys
- Shows the result with execution time in µs
- Automatically verifies the round-trip: `decrypt(encrypt(PT)) == PT`

---

### Tab 2 — Avalanche Analysis

> Flip a single bit and watch ~50% of the ciphertext change.

![Avalanche Tab](tab2_avalanche.png)

- Flip any bit (0–63) in the plaintext or the key
- Colour-coded bit bar shows exactly which ciphertext bits changed
- Displays both ciphertexts, XOR difference, and a quality rating

---

### Tab 3 — Key Size Comparison

> Encrypt the same plaintext with an 80-bit and a 128-bit key side by side.

![Key Comparison Tab](tab3_compare.png)

- Compares outputs, timing, and security levels
- Shows how many bits differ between the two ciphertexts

---

## Project Structure

```
├── rectangle_cipher.py   # Cipher engine — all functions, test vectors, docs
├── rectangle_app.py      # Streamlit interactive web application
└── README.md
```

---

## Getting Started

```bash
pip install streamlit
streamlit run rectangle_app.py
```

---

## Verified Test Vectors

All four official test vectors from the original paper pass:

| Variant    | Plaintext          | Key                              | Expected Ciphertext |
|------------|--------------------|----------------------------------|---------------------|
| REC-80 ×0  | 0000000000000000   | 00000000000000000000             | 2D96E354E8B10874    |
| REC-80 ×F  | FFFFFFFFFFFFFFFF   | FFFFFFFFFFFFFFFFFFFF             | 9945AA34AE3D0112    |
| REC-128 ×0 | 0000000000000000   | 0000...0000 (32 chars)           | AEE6361344A499EE    |
| REC-128 ×F | FFFFFFFFFFFFFFFF   | FFFF...FFFF (32 chars)           | E83EEFEE4A157A46    |

---

## Authors

**Reem AL-ZOUHBY** · **Mariam MARHABA**  
Supervised by **Dr. Abed Ellatif Samhat**

---

## Reference

W. Zhang, Z. Bao, D. Lin, V. Rijmen, B. Yang, and I. Verbauwhede, *"RECTANGLE: A Bit-slice Lightweight Block Cipher Suitable for Multiple Platforms"*, SCIENCE CHINA Information Sciences, 2015.  
[https://eprint.iacr.org/2014/084.pdf](https://eprint.iacr.org/2014/084.pdf)
