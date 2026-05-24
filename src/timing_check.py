# src/timing_check.py
"""
Compare a recent result (JSON) against a baseline CSV or baseline JSON.
Simple CLI: pass --recent <file> --baseline <file> --threshold <float>
If recent_mean > baseline_mean * threshold, exit code 2.
"""

import argparse
import csv
import json
import sys

def load_recent_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_baseline_csv(path: str):
    # Expect baseline csv with header including mean_s and impl/iterations
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--recent", required=True)
    p.add_argument("--baseline", required=True)
    p.add_argument("--threshold", type=float, default=1.05)
    args = p.parse_args()

    recent = load_recent_json(args.recent)
    recent_mean = recent["result"].get("mean_s") or recent["result"].get("median_s")
    if recent_mean is None:
        print("No mean/median found in recent result")
        sys.exit(1)

    # allow baseline to be CSV (pick matching row) or JSON with meta.mean
    if args.baseline.endswith(".json"):
        with open(args.baseline, encoding="utf-8") as f:
            b = json.load(f)
        baseline_mean = b["result"].get("mean_s") or b["result"].get("median_s")
    else:
        rows = load_baseline_csv(args.baseline)
        # attempt to find a matching row by impl and iterations in recent meta
        meta = recent.get("meta", {})
        impl = meta.get("impl")
        iterations = str(meta.get("iterations"))
        baseline_mean = None
        for r in rows:
            if impl and r.get("impl") != impl:
                continue
            if iterations and r.get("iterations") and r.get("iterations") != iterations:
                continue
            # pick the first matching row
            val = r.get("mean_s") or r.get("median_s")
            if val:
                try:
                    baseline_mean = float(val)
                    break
                except Exception:
                    pass
        if baseline_mean is None and rows:
            # fallback: use first row mean
            try:
                baseline_mean = float(rows[0].get("mean_s") or rows[0].get("median_s"))
            except Exception:
                baseline_mean = None

    if baseline_mean is None:
        print("Could not determine baseline mean")
        sys.exit(1)

    print(f"recent_mean: {recent_mean:.6f}s, baseline_mean: {baseline_mean:.6f}s, threshold: {args.threshold}")
    if recent_mean > baseline_mean * args.threshold:
        print("REGRESSION: recent mean exceeds baseline * threshold")
        sys.exit(2)
    else:
        print("OK: within threshold")
        sys.exit(0)

if __name__ == "__main__":
    main()