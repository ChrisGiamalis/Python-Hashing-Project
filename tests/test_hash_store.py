# tests/test_hash_store.py
from src.hash_store import create_user, verify_login, rehash_on_use
from src.hashlib_impl import gen_salt, iterative_hash

def test_create_and_verify():
    store = {}
    create_user(store, "u", "pw", iterations=2, algo="sha256")
    assert verify_login(store, "u", "pw") is True
    assert verify_login(store, "u", "wrong") is False

def test_rehash_on_use_updates_iterations():
    store = {}
    create_user(store, "u", "pw", iterations=1, algo="sha256")
    assert verify_login(store, "u", "pw")
    ok = rehash_on_use(store, "u", "pw", new_iterations=5, rotate_salt=False)
    assert ok is True
    assert store["u"]["iterations"] == 5

def test_deterministic_iterative_hash():
    salt = gen_salt(8)
    a = iterative_hash("hello", salt, iterations=3, algo="sha256")
    b = iterative_hash("hello", salt, iterations=3, algo="sha256")
    assert a == b