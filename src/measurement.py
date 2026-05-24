# src/measurement.py
"""
Simple measurement utilities: warmup + repeated timing, CSV/JSON writers.
"""

from typing import Callable, Sequence, Dict, Any, Optional
import time
import statistics
import csv
import json
import os

try:
    import psutil
except Exception:
    psutil = None

def measure(func: Callable, args: Sequence = (), kwargs: Optional[Dict] = None,
            *, warmup: int = 5, runs: int = 50, sample_psutil: bool = False) -> Dict[str, Any]:
    kwargs = kwargs or {}
    for _ in range(max(0, warmup)):
        func(*args, **kwargs)
    times = []
    cpu_samples = []
    mem_samples = []
    for _ in range(max(1, runs)):
        if psutil and sample_psutil:
            p = psutil.Process()
            cpu_before = p.cpu_percent(interval=None)
            mem_before = p.memory_info().rss
        t0 = time.perf_counter()
        func(*args, **kwargs)
        dt = time.perf_counter() - t0
        times.append(dt)
        if psutil and sample_psutil:
            cpu_after = p.cpu_percent(interval=None)
            mem_after = p.memory_info().rss
            cpu_samples.append(max(0.0, cpu_after - cpu_before))
            mem_samples.append(max(0, mem_after - mem_before))
    res = {
        "runs": runs,
        "warmup": warmup,
        "mean_s": statistics.mean(times) if times else None,
        "median_s": statistics.median(times) if times else None,
        "stdev_s": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min_s": min(times) if times else None,
        "max_s": max(times) if times else None,
        "raw_times_s": times,
    }
    if sample_psutil and psutil:
        res.update({
            "cpu_samples": cpu_samples,
            "mem_samples": mem_samples,
            "mean_cpu_delta": statistics.mean(cpu_samples) if cpu_samples else None,
            "mean_mem_delta": statistics.mean(mem_samples) if mem_samples else None,
        })
    return res

def write_json(path: str, data: Dict[str, Any]) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=list)

def write_csv_row(path: str, header: Sequence[str], row: Sequence[Any]) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(header)
        w.writerow(row)