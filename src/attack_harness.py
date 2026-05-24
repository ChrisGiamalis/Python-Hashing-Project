# src/attack_harness.py
"""
Matrix-driven experiment harness.
Reads rows describing parameter sets and runs measurement for each combination.
This is a compact example; adapt matrix source and output formatting as needed.
"""

import csv
import json
import os
import time
from typing import Dict, Callable, Any
from .measurement import measure, write_json
from .hash_store import create_user, verify_login, rehash_on_use
from . import core, hashlib_impl

IMPLEMENTATIONS: Dict[str, Callable[..., bytes]] = {
    "core": lambda pw, salt, iterations=1, algo="": core.iterative_hash_hex(pw, rounds=max(1, iterations)),
    # hashlib_impl.iterative_hash returns bytes; we use lambda to normalize signature if needed
    "hashlib": lambda pw, salt, iterations=1, algo="sha256": hashlib_impl.iterative_hash(pw, salt, iterations=iterations, algo=algo)
}

def run_matrix(matrix_path: str, out_dir: str = "experiments/results"):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(matrix_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # expected columns: impl,iterations,runs,warmup,username,password
            impl = row.get("impl", "hashlib")
            iterations = int(row.get("iterations", 1))
            runs = int(row.get("runs", 100))
            warmup = int(row.get("warmup", 10))
            username = row.get("username", f"user{i}")
            password = row.get("password", "password")
            algo = row.get("algo", "sha256")
            # prepare store and user
            store = {}
            create_user(store, username, password, iterations=1, algo=algo)  # seed with base user (1 iter)
            # measure verify (use verify_login wrapper)
            func = lambda: verify_login(store, username, password)
            result = measure(func, warmup=warmup, runs=runs, sample_psutil=False)
            meta = {
                "matrix_row": row,
                "impl": impl,
                "iterations": iterations,
                "runs": runs,
                "warmup": warmup,
                "username": username,
                "algo": algo,
                "timestamp": time.time()
            }
            out = {"meta": meta, "result": result}
            out_path = os.path.join(out_dir, f"matrix_row_{i}_{impl}_it{iterations}.json")
            write_json(out_path, out)
            print("Wrote:", out_path)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--matrix", default="experiments/matrix.csv")
    p.add_argument("--out", default="experiments/results")
    args = p.parse_args()
    run_matrix(args.matrix, args.out)