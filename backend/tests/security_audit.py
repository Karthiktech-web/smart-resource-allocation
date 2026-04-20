"""
Security audit script for Smart Resource Allocation backend.
Run this locally against a running service to verify API exposure, CORS, injection resilience, rate limiting, and write endpoint auth.
"""

import json
import os
import sys
from typing import List

import requests

BASE_URL = os.environ.get("SRA_BASE_URL", "http://127.0.0.1:8000")

ENDPOINTS = [
    ("/", "Root"),
    ("/health", "Health"),
    ("/api/programs", "Programs"),
    ("/api/needs", "Needs"),
    ("/api/areas/priorities", "Area Priorities"),
    ("/api/areas/heatmap/data", "Heatmap"),
    ("/api/allocation/gaps", "Allocation Gaps"),
    ("/api/allocation/recommend", "Allocation Recommend"),
]

INJECTION_PAYLOADS = [
    "'; DROP TABLE users; --",
    "<script>alert(1)</script>",
    "../../../etc/passwd",
    "1 OR 1=1",
    "admin' --",
]

WRITE_ENDPOINTS = [
    ("POST", "/api/allocation/approve", {}),
    ("POST", "/api/programs", {"name": "Unauthorized Program"}),
    ("POST", "/api/needs", {"title": "Unauthorized Check"}),
]


def check_endpoints() -> None:
    print("\n1. Checking public API endpoints...")
    for path, name in ENDPOINTS:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
            print(f"   {name}: {response.status_code}")
        except Exception as exc:
            print(f"   {name}: ERROR -> {exc}")


def check_cors() -> None:
    print("\n2. Checking CORS configuration...")
    try:
        response = requests.options(
            f"{BASE_URL}/api/programs",
            headers={
                "Origin": "http://evil-site.com",
                "Access-Control-Request-Method": "GET",
            },
            timeout=10,
        )
        origin = response.headers.get("access-control-allow-origin", "")
        if origin == "*":
            print("   WARN: CORS allows all origins (*). Restrict for production.")
        elif "evil-site.com" in origin:
            print("   FAIL: CORS allows arbitrary origins!")
        else:
            print(f"   PASS: CORS appears restricted: {origin or 'none'}")
    except Exception as exc:
        print(f"   ERROR: CORS check failed -> {exc}")


def check_injection() -> None:
    print("\n3. Testing for injection vulnerabilities...")
    for payload in INJECTION_PAYLOADS:
        try:
            response = requests.get(
                f"{BASE_URL}/api/needs",
                params={"category": payload},
                timeout=10,
            )
            status = response.status_code
            body = response.text[:200].replace("\n", " ")
            print(f"   Payload [{payload[:30]}...]: {status} -> {body}")
        except Exception as exc:
            print(f"   Payload [{payload[:30]}...]: ERROR -> {exc}")


def check_rate_limiting() -> None:
    print("\n4. Testing rate limiting behavior...")
    statuses = []
    for i in range(12):
        try:
            response = requests.get(f"{BASE_URL}/api/dashboard", timeout=10)
            statuses.append(response.status_code)
        except Exception as exc:
            statuses.append(None)
            print(f"   Request {i + 1}: ERROR -> {exc}")
    limited = any(code == 429 for code in statuses if code is not None)
    print(f"   Rate limiting {'detected' if limited else 'not detected'}")
    print(f"   Status codes: {statuses}")


def check_write_auth() -> None:
    print("\n5. Checking auth enforcement on write endpoints...")
    for method, path, payload in WRITE_ENDPOINTS:
        try:
            if method == "POST":
                response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=10)
            else:
                response = requests.request(method, f"{BASE_URL}{path}", json=payload, timeout=10)
            status = response.status_code
            print(f"   {method} {path}: {status} -> {response.text[:200].replace('\n', ' ')}")
        except Exception as exc:
            print(f"   {method} {path}: ERROR -> {exc}")


def check_dockerignore() -> None:
    print("\n6. Checking .dockerignore for sensitive files...")
    dockerignore_path = os.path.join(os.path.dirname(__file__), "..", ".dockerignore")
    if os.path.exists(dockerignore_path):
        with open(dockerignore_path, "r", encoding="utf-8") as dockerignore:
            contents = dockerignore.read()
        if "*.json" in contents or ".env" in contents or "firebase" in contents:
            print("   PASS: Sensitive and build-irrelevant files are ignored.")
        else:
            print("   WARN: .dockerignore exists but may not include all sensitive file patterns.")
    else:
        print("   WARN: .dockerignore not found in backend folder.")


def main() -> int:
    print("========== SRA SECURITY AUDIT ==========")
    print(f"Target: {BASE_URL}")
    check_endpoints()
    check_cors()
    check_injection()
    check_rate_limiting()
    check_write_auth()
    check_dockerignore()
    print("\n========== AUDIT COMPLETE ==========")
    return 0


if __name__ == "__main__":
    sys.exit(main())
