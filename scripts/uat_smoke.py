import json
import os
import sys
from datetime import datetime, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from App.main import create_app
from App.controllers.initialize import initialize
from App.models import Resident


def _post_form(client, path: str, data: dict, follow_redirects: bool = False):
    return client.post(path, data=data, follow_redirects=follow_redirects)


def _post_json(client, path: str, payload: dict):
    return client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
    )


def run():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_COOKIE_SECURE": False,
        }
    )

    # Seed demo data into the in-memory DB
    with app.app_context():
        initialize()
        alice = Resident.query.filter_by(username="alice").first()
        if not alice:
            raise RuntimeError("Seed data missing resident 'alice'.")
        alice_area_id = alice.areaId
        alice_street_id = alice.streetId

    results = []

    with app.test_client() as client:
        # 1) Login (Admin)
        r = client.get("/login")
        results.append(("AUTH-LOGIN-PAGE", r.status_code == 200, f"GET /login -> {r.status_code}"))

        r = _post_form(client, "/login", {"username": "admin", "password": "adminpass"})
        results.append(("AUTH-LOGIN-ADMIN", r.status_code in (302, 200), f"POST /login admin -> {r.status_code}"))

        r = client.get("/api/identify")
        results.append(("AUTH-IDENTIFY", r.status_code == 200, f"GET /api/identify -> {r.status_code}"))

        r = client.get("/portal/admin")
        results.append(("ADMIN-PORTAL-PAGE", r.status_code == 200, f"GET /portal/admin -> {r.status_code}"))

        # 2) Admin actions (areas/streets)
        r = _post_json(client, "/admin/areas", {"name": "UAT Area"})
        ok = r.status_code == 201
        results.append(("ADMIN-ADD-AREA", ok, f"POST /admin/areas -> {r.status_code}"))

        area_id = None
        if ok:
            area_id = r.get_json().get("id")

        r = _post_json(client, "/admin/streets", {"name": "UAT Street", "area_id": area_id or 1})
        ok = r.status_code == 201
        results.append(("ADMIN-ADD-STREET", ok, f"POST /admin/streets -> {r.status_code}"))

        street_id = None
        if ok:
            street_id = r.get_json().get("id")

        # create a driver via admin API (covers admin driver creation)
        r = _post_json(client, "/admin/drivers", {"username": "uat_driver", "password": "uatpass"})
        ok = r.status_code in (201, 409)
        results.append(("ADMIN-CREATE-DRIVER", ok, f"POST /admin/drivers -> {r.status_code}"))

        # logout
        client.get("/logout")

        # 3) Driver flow (bob)
        _post_form(client, "/login", {"username": "bob", "password": "bobpass"})
        r = client.get("/api/identify")
        results.append(("DRIVER-LOGIN", r.status_code == 200, f"Driver identify -> {r.status_code}"))

        r = client.get("/portal/driver")
        results.append(("DRIVER-PORTAL-PAGE", r.status_code == 200, f"GET /portal/driver -> {r.status_code}"))

        # schedule a drive within 60 days
        dt = datetime.now() + timedelta(days=7)
        date_str = dt.strftime("%Y-%m-%d")
        time_str = "10:00"

        r = _post_json(
            client,
            "/driver/drives",
            {
                # Drive must match resident area/street for stop requests
                "area_id": alice_area_id,
                "street_id": alice_street_id,
                "date": date_str,
                "time": time_str,
            },
        )
        ok = r.status_code == 201
        results.append(("DRIVER-SCHEDULE", ok, f"POST /driver/drives -> {r.status_code}"))

        drive_id = None
        if ok:
            drive_id = r.get_json().get("id")

        # schedule a second drive, then cancel it (covers cancel flow)
        r2 = _post_json(
            client,
            "/driver/drives",
            {"area_id": alice_area_id, "street_id": alice_street_id, "date": date_str, "time": "11:00"},
        )
        cancel_drive_id = r2.get_json().get("id") if r2.status_code == 201 else None
        r2c = client.post(f"/driver/drives/{cancel_drive_id}/cancel") if cancel_drive_id else r2
        ok = cancel_drive_id is not None and r2c.status_code == 200
        results.append(("DRIVER-CANCEL", ok, f"POST /driver/drives/{cancel_drive_id}/cancel -> {getattr(r2c, 'status_code', 'n/a')}"))

        # logout driver (resident must request stop while drive is still Upcoming)
        client.get("/logout")

        # 4) Resident flow (alice) - subscribe + request stop (Upcoming)
        _post_form(client, "/login", {"username": "alice", "password": "alicepass"})
        r = client.get("/api/identify")
        results.append(("RESIDENT-LOGIN", r.status_code == 200, f"Resident identify -> {r.status_code}"))

        r = client.get("/portal/resident")
        results.append(("RESIDENT-PORTAL-PAGE", r.status_code == 200, f"GET /portal/resident -> {r.status_code}"))

        r = _post_json(client, "/resident/subscriptions", {"drive_id": drive_id})
        ok = r.status_code in (201, 200)
        results.append(("RESIDENT-SUBSCRIBE", ok, f"POST /resident/subscriptions -> {r.status_code}"))

        r = _post_json(client, "/resident/stops", {"drive_id": drive_id})
        ok = r.status_code == 201
        results.append(("RESIDENT-REQUEST-STOP", ok, f"POST /resident/stops -> {r.status_code}"))

        # logout resident
        client.get("/logout")

        # 5) Driver starts + ends drive (should trigger notifications)
        _post_form(client, "/login", {"username": "bob", "password": "bobpass"})
        r = client.post(f"/driver/drives/{drive_id}/start")
        ok = r.status_code == 200
        results.append(("DRIVER-START", ok, f"POST /driver/drives/{drive_id}/start -> {r.status_code}"))

        r = client.post(f"/driver/drives/{drive_id}/end")
        ok = r.status_code == 200
        results.append(("DRIVER-END", ok, f"POST /driver/drives/{drive_id}/end -> {r.status_code}"))

        client.get("/logout")

        # 6) Resident inbox should be accessible and contain messages
        _post_form(client, "/login", {"username": "alice", "password": "alicepass"})

        r = client.get("/resident/inbox")
        items = []
        try:
            items = (r.get_json() or {}).get("items") or []
        except Exception:
            items = []
        ok = r.status_code == 200 and len(items) > 0
        results.append((
            "RESIDENT-INBOX",
            ok,
            f"GET /resident/inbox -> {r.status_code} (items={len(items)})",
        ))

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)

    print(f"UAT smoke checks: {passed}/{total} passed")
    for key, ok, note in results:
        print(f"- {key}: {'PASS' if ok else 'FAIL'} ({note})")

    # Exit non-zero if any fail (handy for CI)
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
