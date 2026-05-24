# tests/test_core.py
import time
import pytest
from src.core import iterative_hash, iterative_hash_hex
from src.measurement import measure

def test_deterministic_same_input():
    a = iterative_hash(b"hello", rounds=3)
    b = iterative_hash("hello", rounds=3)
    assert a == b
    assert iterative_hash_hex("hello", rounds=3) == a.hex()

def test_rounds_change_output():
    out1 = iterative_hash("x", rounds=1)
    out2 = iterative_hash("x", rounds=2)
    assert out1 != out2

def test_output_length_and_type():
    raw = iterative_hash("data", rounds=1)
    assert isinstance(raw, (bytes, bytearray))
    assert len(raw) == 8

def test_empty_input_stable():
    a = iterative_hash("", rounds=5)
    b = iterative_hash(b"", rounds=5)
    assert a == b

@pytest.mark.timeout(5)
def test_timing_smoke():
    func = lambda: iterative_hash("benchmark-input", rounds=10)
    res = measure(func, warmup=2, runs=50, sample_psutil=False)
    assert res["mean_s"] is not None
    # Permissive threshold; adjust for your CI/hardware
    assert res["mean_s"] < 1.0