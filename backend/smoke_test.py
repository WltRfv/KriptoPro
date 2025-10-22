import os
import uuid
from app import create_app, db

# Ensure dev mode to avoid real email sending
os.environ.setdefault("FLASK_ENV", "development")

app = create_app()

results = {}

with app.app_context():
    # Ensure tables exist
    db.create_all()

    client = app.test_client()

    # 1) Basic admin status
    resp = client.get("/api/admin/system-status")
    results["admin_status_code"] = resp.status_code
    try:
        results["admin_status_json"] = resp.get_json()
    except Exception:
        results["admin_status_json"] = None

    # 2) Register a user
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "Passw0rd!"
    resp = client.post("/api/auth/register", json={
        "email": email,
        "password": password
    })
    results["register_status_code"] = resp.status_code
    results["register_json"] = resp.get_json()

    # 3) Login
    resp = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    results["login_status_code"] = resp.status_code
    login_json = resp.get_json()
    results["login_json"] = login_json

    token = None
    if isinstance(login_json, dict):
        token = login_json.get("access_token")

    # 4) Authenticated wallet balance endpoint
    if token:
        resp = client.get("/api/wallet/balance", headers={
            "Authorization": f"Bearer {token}"
        })
        results["wallet_balance_status_code"] = resp.status_code
        results["wallet_balance_json"] = resp.get_json()
    else:
        results["wallet_balance_status_code"] = None
        results["wallet_balance_json"] = None

print(results)
