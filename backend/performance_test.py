import requests
import time
import statistics

BASE_URL = "http://127.0.0.1:8003"

endpoints = [
    ("GET", "/", None),
    ("GET", "/health", None),
]

print("Performance Test Results")
print("=" * 60)

for method, path, data in endpoints:
    times = []
    for _ in range(5):
        url = f"{BASE_URL}{path}"
        print(f"Calling {url}")

        start = time.time()

        if method == "GET":
            r = requests.get(url)
        else:
            r = requests.post(url, json=data)

        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

    avg = statistics.mean(times)
    p95 = sorted(times)[int(len(times) * 0.95)]

    print(f"{method} {path} → avg: {avg:.2f} ms | p95: {p95:.2f} ms")