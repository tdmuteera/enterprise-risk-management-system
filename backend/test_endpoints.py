"""Comprehensive API endpoint test suite."""
import httpx
import json
import sys

BASE = "http://localhost:8000/api/v1"
CLIENT = httpx.Client(timeout=30.0, follow_redirects=True)
results = []

def test(name, response, show_detail=False):
    ok = 200 <= response.status_code < 300
    status = "PASS" if ok else "FAIL"
    results.append((name, response.status_code, status))
    print(f"  [{status}] {name}: {response.status_code}")
    if not ok or show_detail:
        try:
            print(f"    -> {json.dumps(response.json(), default=str)[:300]}")
        except Exception:
            print(f"    -> {response.text[:300]}")
    return ok

def main():
    print("=" * 60)
    print("ERM System - API Endpoint Test Suite")
    print("=" * 60)

    # 1. Authentication
    print("\n--- Authentication ---")
    r = CLIENT.post(f"{BASE}/auth/login", json={"email": "admin@erm.edu", "password": "AdminPass123!"})
    test("POST /auth/login (admin)", r)
    if r.status_code != 200:
        print("Cannot proceed without auth token!")
        sys.exit(1)
    admin_token = r.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    r = CLIENT.get(f"{BASE}/auth/me", headers=admin_headers)
    test("GET /auth/me", r)
    user_data = r.json()
    print(f"    User: {user_data.get('full_name')}, Role: {user_data.get('role')}")

    # Login as clerk
    r = CLIENT.post(f"{BASE}/auth/login", json={"email": "user.fin@erm.edu", "password": "FinUser123!"})
    test("POST /auth/login (clerk)", r)
    clerk_token = r.json()["access_token"] if r.status_code == 200 else None
    clerk_headers = {"Authorization": f"Bearer {clerk_token}"} if clerk_token else {}

    # Login as risk officer
    r = CLIENT.post(f"{BASE}/auth/login", json={"email": "risk.officer@erm.edu", "password": "RiskOff123!"})
    test("POST /auth/login (officer)", r)
    officer_token = r.json()["access_token"] if r.status_code == 200 else None
    officer_headers = {"Authorization": f"Bearer {officer_token}"} if officer_token else {}

    # 2. Departments
    print("\n--- Departments ---")
    r = CLIENT.get(f"{BASE}/departments", headers=admin_headers)
    test("GET /departments", r)
    departments = r.json() if r.status_code == 200 else []
    dept_id = departments[0]["id"] if departments else None
    if dept_id:
        print(f"    First dept: {departments[0]['name']} (id: {dept_id})")

    if dept_id:
        r = CLIENT.get(f"{BASE}/departments/{dept_id}/risks", headers=admin_headers)
        test(f"GET /departments/{{id}}/risks", r)

    # 3. Users
    print("\n--- Users ---")
    r = CLIENT.get(f"{BASE}/users", headers=admin_headers)
    test("GET /users (admin)", r)

    # 4. Risks - List & Filter
    print("\n--- Risks (List & Filter) ---")
    r = CLIENT.get(f"{BASE}/risks/", headers=admin_headers)
    test("GET /risks/", r)
    risk_id = None
    if r.status_code == 200:
        data = r.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(items, list) and items:
            risk_id = items[0]["id"]
            print(f"    Total risks: {data.get('total', len(items))}")

    r = CLIENT.get(f"{BASE}/risks/", params={"category": "Financial"}, headers=admin_headers)
    test("GET /risks/?category=Financial", r)

    r = CLIENT.get(f"{BASE}/risks/", params={"status": "Open"}, headers=admin_headers)
    test("GET /risks/?status=Open", r)

    r = CLIENT.get(f"{BASE}/risks/", params={"page": 1, "page_size": 5, "sort_by": "created_at", "order": "desc"}, headers=admin_headers)
    test("GET /risks/ (paginated)", r)

    # 5. Risks - Single Detail
    print("\n--- Risk Detail ---")
    if risk_id:
        r = CLIENT.get(f"{BASE}/risks/{risk_id}", headers=admin_headers)
        ok = test(f"GET /risks/{{id}}", r)
        if ok:
            d = r.json()
            print(f"    Title: {d.get('title')}")
            print(f"    risk_type: {d.get('risk_type')}, audit_trail: {len(d.get('audit_trail', []))}")
            print(f"    linked_risks: {len(d.get('linked_risks', []))}")
            print(f"    recommendations: {len(d.get('recommendations', []))}")

    # 6. Pending Risks
    print("\n--- Pending Risks ---")
    r = CLIENT.get(f"{BASE}/risks/pending", headers=admin_headers)
    test("GET /risks/pending (admin)", r)

    # 7. Risk Mitigations
    print("\n--- Mitigations ---")
    if risk_id:
        r = CLIENT.get(f"{BASE}/risks/{risk_id}/mitigations", headers=admin_headers)
        test("GET /risks/{id}/mitigations", r)

    # 8. Recommendations
    print("\n--- Recommendations ---")
    if risk_id:
        r = CLIENT.get(f"{BASE}/risks/{risk_id}/recommendations", headers=admin_headers)
        test("GET /risks/{id}/recommendations", r)

    # 9. Analytics
    print("\n--- Analytics ---")
    r = CLIENT.get(f"{BASE}/analytics/institutional-summary", headers=admin_headers)
    test("GET /analytics/institutional-summary", r)

    r = CLIENT.get(f"{BASE}/analytics/trend", headers=admin_headers)
    test("GET /analytics/trend", r)

    r = CLIENT.get(f"{BASE}/analytics/heatmap", headers=admin_headers)
    test("GET /analytics/heatmap", r)

    # 10. Alerts
    print("\n--- Alerts ---")
    r = CLIENT.get(f"{BASE}/alerts", headers=admin_headers)
    test("GET /alerts", r)

    r = CLIENT.get(f"{BASE}/alerts/unread-count", headers=admin_headers)
    test("GET /alerts/unread-count", r)

    # 11. Audit Logs
    print("\n--- Audit Logs ---")
    r = CLIENT.get(f"{BASE}/audit-logs/", headers=admin_headers)
    test("GET /audit-logs/", r)

    r = CLIENT.get(f"{BASE}/audit-logs/domain", headers=admin_headers)
    test("GET /audit-logs/domain", r)

    # 12. Create Risk (as clerk) -> Approval Workflow
    print("\n--- Risk Creation & Approval Workflow ---")
    if clerk_headers and dept_id:
        clerk_me = CLIENT.get(f"{BASE}/auth/me", headers=clerk_headers).json()
        new_risk_payload = {
            "title": "Test Risk - Integration Test",
            "description": "This is a test risk created by the integration test suite to validate the approval workflow.",
            "category": "Financial",
            "department_id": dept_id,
            "owner_id": clerk_me.get("id"),
            "likelihood": 3,
            "impact": 4,
            "velocity": 2,
            "detectability": 3,
        }
        r = CLIENT.post(f"{BASE}/risks/", json=new_risk_payload, headers=clerk_headers)
        test("POST /risks/ (clerk creates risk)", r)
        if r.status_code in (200, 201):
            new_risk = r.json()
            new_risk_id = new_risk["id"]
            print(f"    Created risk status: {new_risk.get('status')}")

            # Approve as officer/admin
            if officer_headers:
                approve_payload = {"justification": "Test approval - risk is properly documented and scored."}
                r = CLIENT.post(f"{BASE}/risks/{new_risk_id}/approve", json=approve_payload, headers=admin_headers)
                test("POST /risks/{id}/approve (admin)", r)
                if r.status_code == 200:
                    print(f"    Approved status: {r.json().get('status')}")

    # 13. Reports
    print("\n--- Reports ---")
    if dept_id:
        r = CLIENT.get(f"{BASE}/reports/department/{dept_id}", params={"format": "excel"}, headers=admin_headers)
        test("GET /reports/department/{id}?format=excel", r)

    r = CLIENT.get(f"{BASE}/reports/institutional", params={"format": "pdf"}, headers=admin_headers)
    test("GET /reports/institutional?format=pdf", r)

    r = CLIENT.get(f"{BASE}/reports/executive", headers=admin_headers)
    test("GET /reports/executive", r)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for _, _, s in results if s == "PASS")
    failed = sum(1 for _, _, s in results if s == "FAIL")
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(results)} tests")
    print("=" * 60)

    if failed > 0:
        print("\nFailed tests:")
        for name, code, status in results:
            if status == "FAIL":
                print(f"  - {name}: HTTP {code}")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
