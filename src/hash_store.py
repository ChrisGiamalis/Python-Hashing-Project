# src/hash_store.py
"""
In-memory user store for salted digests and iterative upgrades.
Store schema: username -> dict with keys: salt_hex, digest_hex, iterations, algo
"""

from typing import Dict, Optional
import hmac
from .hashlib_impl import gen_salt, iterative_hash, to_hex, from_hex

Store = Dict[str, Dict[str, object]]

def create_user(store: Store, username: str, password: str, iterations: int = 1, algo: str = "sha256", salt_len: int = 16) -> None:
    salt = gen_salt(salt_len)
    digest = iterative_hash(password, salt, iterations=iterations, algo=algo)
    store[username] = {
        "salt_hex": to_hex(salt),
        "digest_hex": to_hex(digest),
        "iterations": int(iterations),
        "algo": algo
    }

def verify_login(store: Store, username: str, password: str) -> bool:
    entry = store.get(username)
    if entry is None:
        return False
    salt = from_hex(entry["salt_hex"])
    stored = from_hex(entry["digest_hex"])
    iterations = int(entry.get("iterations", 1))
    algo = entry.get("algo", "sha256")
    computed = iterative_hash(password, salt, iterations=iterations, algo=algo)
    return hmac.compare_digest(computed, stored)

def rehash_on_use(store: Store, username: str, password: str, new_iterations: int, rotate_salt: bool = False, salt_len: int = 16) -> bool:
    entry = store.get(username)
    if entry is None:
        return False
    salt = from_hex(entry["salt_hex"])
    stored = from_hex(entry["digest_hex"])
    iterations = int(entry.get("iterations", 1))
    algo = entry.get("algo", "sha256")
    computed = iterative_hash(password, salt, iterations=iterations, algo=algo)
    if not hmac.compare_digest(computed, stored):
        return False
    # verified, now upgrade
    if rotate_salt:
        salt = gen_salt(salt_len)
    new_digest = iterative_hash(password, salt, iterations=new_iterations, algo=algo)
    entry.update({
        "salt_hex": to_hex(salt),
        "digest_hex": to_hex(new_digest),
        "iterations": int(new_iterations),
        "algo": algo
    })
    return True