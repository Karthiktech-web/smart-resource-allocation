"""
Load test script for Smart Resource Allocation backend.
Simulate concurrent users hitting key read endpoints and summarize response latency.
"""

import threading
import time
from collections import defaultdict
import statistics
import os
import sys

import requests

BASE_URL = os.environ.get("SRA_BASE_URL", "http://127.0.0.1:8000")
CONCURRENT_USERS = int(os.environ.get("SRA_CONCURRENT_USERS", 10))
REQUESTS_PER_USER = int(os.environ.get("SRA_REQUESTS_PER_USER", 5))

ENDPOINTS = [
    "/",
    "/health",
    "/api/programs",
    "/api/needs",
    "/api/areas/priorities",
    "/api/areas/heatmap/data",
]

results = defaultdict(list)
errors = defaultdict(int)
lock = threading.Lock()


def simulate_user(user_id: int) -> None:
    for i in range(REQUESTS_PER_USER):
        for path in ENDPOINTS:
            url = f"{BASE_URL}{path}"
            start = time.perf_counter()
            try:
                response = requests.get(url, timeout=15)
                elapsed = (time.perf_counter() - start) * 1000
                with lock:
                    results[path].append(elapsed)
                    if response.status_code >= 400:
                        errors[path] += 1
            except Exception:
                elapsed = (time.perf_counter() - start) * 1000
                with lock:
                    results[path].append(elapsed)
                    errors[path] += 1


def summarize() -> None:
    total_requests = sum(len(times) for times in results.values())
    total_errors = sum(errors.values())
    duration = sum(sum(times) for times in results.values()) / 1000

    print(f"\nLoad Test Summary")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Concurrent users: {CONCURRENT_USERS}")
    print(f"Requests per user: {REQUESTS_PER_USER}")
    print(f"Total requests: {total_requests}")
    print(f"Total errors: {total_errors}")
    print("\nEndpoint performance:\n")
    print(f"{ 'Endpoint':<35} {'Avg(ms)':<10} {'P95(ms)':<10} {'Max(ms)':<10} {'Errors':<8}")
    print("-" * 80)
    for path, times in sorted(results.items()):
        if times:
            avg = statistics.mean(times)
            p95 = statistics.quantiles(times, n=100)[94]
            mx = max(times)
        else:
            avg = p95 = mx = 0.0
        print(f"{path:<35} {avg:<10.0f} {p95:<10.0f} {mx:<10.0f} {errors[path]:<8}")
    print("\nLoad test complete.")


def main() -> int:
    print("Starting load test...")
    threads = []
    start_time = time.time()

    for user_id in range(CONCURRENT_USERS):
        thread = threading.Thread(target=simulate_user, args=(user_id,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_time = time.time() - start_time
    print(f"Completed in {total_time:.1f}s")
    summarize()
    return 0


if __name__ == "__main__":
    sys.exit(main())
