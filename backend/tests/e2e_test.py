
import requests

BASE_URL = "http://127.0.0.1:8002"

def test_basic_flow():
    print("\n===== E2E BASIC TEST =====\n")

    # 1. Root
    r = requests.get(f"{BASE_URL}/")
    print("Root:", r.status_code, r.json())

    # 2. Health
    r = requests.get(f"{BASE_URL}/health")
    print("Health:", r.status_code, r.json())

    print("\n===== TEST COMPLETE =====\n")

if __name__ == "__main__":
    test_basic_flow()