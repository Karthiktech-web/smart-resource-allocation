import requests

BASE_URL = "http://127.0.0.1:8003"

def test_full_flow():
    print("\n===== FULL E2E TEST =====\n")

    endpoints = [
        ("/", "Root"),
        ("/health", "Health"),
        ("/api/programs", "Programs"),
        ("/api/needs", "Needs"),
        ("/api/areas/priorities", "Area Priorities"),
        ("/api/areas/heatmap/data", "Heatmap"),
        ("/api/allocation/gaps", "Gaps"),
        ("/api/allocation/recommend", "Recommendation"),
    ]

    for path, name in endpoints:
        try:
            r = requests.get(f"{BASE_URL}{path}")
            print(f"{name}: {r.status_code} {r.json()}")
        except Exception as e:
            print(f"{name}: ERROR → {e}")

    print("\n===== TEST COMPLETE =====\n")


if __name__ == "__main__":
    test_full_flow()