# src/scripts/experiment.py
"""
CLI experiment runner.
Run as: python -m src.scripts.experiment --impl hashlib --username alice --password hunter2 --iterations 10 --runs 200 --warmup 20 --out out.json
"""

import argparse
import time
from ..hash_store import create_user, verify_login
from ..measurement import measure, write_json

def run_single(impl: str, username: str, password: str, iterations: int, runs: int, warmup: int, out: str, algo: str = "sha256"):
    store = {}
    # create the user with target iterations so verification uses that iteration count
    create_user(store, username, password, iterations=iterations, algo=algo)
    func = lambda: verify_login(store, username, password)
    res = measure(func, warmup=warmup, runs=runs, sample_psutil=False)
    meta = {
        "impl": impl,
        "username": username,
        "iterations": iterations,
        "runs": runs,
        "warmup": warmup,
        "algo": algo,
        "timestamp": time.time()
    }
    write_json(out, {"meta": meta, "result": res})
    print("Saved:", out)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--impl", default="hashlib")
    p.add_argument("--username", default="alice")
    p.add_argument("--password", default="hunter2")
    p.add_argument("--iterations", "-i", type=int, default=1)
    p.add_argument("--runs", type=int, default=100)
    p.add_argument("--warmup", type=int, default=10)
    p.add_argument("--algo", default="sha256")
    p.add_argument("--out", default="experiments/results/recent_result.json")
    args = p.parse_args()
    run_single(args.impl, args.username, args.password, args.iterations, args.runs, args.warmup, args.out, algo=args.algo)

if __name__ == "__main__":
    main()