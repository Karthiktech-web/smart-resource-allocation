import requests
import time
import statistics

BASE_URL = "http://127.0.0.1:8001"

endpoints = [
    ("GET", "/", None),
    ("GET", "/health", None),
]

print("Performance Test Results")
print("=" * 50)

for method, path, data in endpoints:
    times = []
    
    for _ in range(5):
        try:
            print(f"Calling {BASE_URL}{path}")
            start = time.time()
            r = requests.get(f"{BASE_URL}{path}", timeout=5)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        except Exception as e:
            print(f"ERROR on {path}: {e}")

    if times:
        avg = statistics.mean(times)
        p95 = sorted(times)[int(len(times) * 0.95)]
        print(f"{method} {path} → avg: {avg:.2f} ms | p95: {p95:.2f} ms")
    else:
        print(f"{method} {path} → FAILED")