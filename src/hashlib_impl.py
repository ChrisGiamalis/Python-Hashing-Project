# src/hashlib_impl.py
"""
Salted single-hash and iterative wrapper using hashlib.
Exports: gen_salt, to_hex, from_hex, iterative_hash, verify_digest
"""

from typing import Union
import hashlib
import hmac
import secrets
import binascii

def gen_salt(n: int = 16) -> bytes:
    return secrets.token_bytes(n)

def to_hex(b: bytes) -> str:
    return binascii.hexlify(b).decode("ascii")

def from_hex(s: str) -> bytes:
    return binascii.unhexlify(s.encode("ascii"))

def single_hash(password: Union[str, bytes], salt: bytes, algo: str = "sha256") -> bytes:
    pw = password if isinstance(password, (bytes, bytearray)) else str(password).encode("utf-8")
    h = hashlib.new(algo)
    h.update(salt)
    h.update(pw)
    return h.digest()

def iterative_hash(password: Union[str, bytes], salt: bytes, iterations: int = 1, algo: str = "sha256") -> bytes:
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    digest = single_hash(password, salt, algo=algo)
    for _ in range(iterations - 1):
        digest = hashlib.new(algo, digest).digest()
    return digest

def verify_digest(stored: bytes, password: Union[str, bytes], salt: bytes, iterations: int = 1, algo: str = "sha256") -> bool:
    computed = iterative_hash(password, salt, iterations=iterations, algo=algo)
    return hmac.compare_digest(computed, stored)

if __name__ == "__main__":
    # Quick smoke
    s = gen_salt()
    d1 = iterative_hash("password", s, iterations=1)
    d2 = iterative_hash("password", s, iterations=2)
    print("iter1:", to_hex(d1))
    print("iter2:", to_hex(d2))