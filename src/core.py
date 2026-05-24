# src/core.py
"""
Lightweight deterministic 64-bit iterative hash used as a baseline for microbenchmarks.
Returns 8 raw bytes (little-endian) from iterative mixing of input bytes.
"""

from typing import Union
import struct

def _to_bytes(x: Union[str, bytes]) -> bytes:
    return x if isinstance(x, (bytes, bytearray)) else str(x).encode("utf-8")

def _u64(x: int) -> int:
    return x & 0xFFFFFFFFFFFFFFFF

def _rotl(x: int, r: int) -> int:
    return _u64((x << r) | (x >> (64 - r)))

def iterative_hash(data: Union[str, bytes], rounds: int = 1000) -> bytes:
    if rounds < 1:
        raise ValueError("rounds must be >= 1")
    b = _to_bytes(data)
    h = 0xcbf29ce484222325  # FNV offset basis
    prime = 0x100000001b3
    for r in range(rounds):
        for by in b:
            h ^= by
            h = _u64(h * prime)
        h ^= _u64(r + 0x9e3779b97f4a7c15)
        h = _rotl(h, 13)
    return struct.pack("<Q", _u64(h))

def iterative_hash_hex(data: Union[str, bytes], rounds: int = 1000) -> str:
    return iterative_hash(data, rounds).hex()

if __name__ == "__main__":
    # simple CLI for quick checks
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("data", nargs="?", default="test")
    p.add_argument("--rounds", "-r", type=int, default=100)
    args = p.parse_args()
    print(iterative_hash_hex(args.data, rounds=args.rounds))