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

    # 5) Multi-signature flow sanity check
    ms_email = f"ms_{uuid.uuid4().hex[:8]}@example.com"
    ms_password = "Passw0rd!"
    team = [f"tm{n}_{uuid.uuid4().hex[:4]}@example.com" for n in range(3)]
    ms_register = client.post("/api/auth/register", json={
        "email": ms_email,
        "password": ms_password,
        "is_multi_signature": True,
        "team_emails": team,
        "threshold": 2,
    })
    results["ms_register_status_code"] = ms_register.status_code
    results["ms_register_json"] = ms_register.get_json()

    # ms_login should request shards
    ms_login = client.post("/api/auth/login", json={
        "email": ms_email,
        "password": ms_password,
    })
    results["ms_login_status_code"] = ms_login.status_code
    results["ms_login_json"] = ms_login.get_json()

    ms_token = None
    if isinstance(results.get("ms_login_json"), dict) and results["ms_login_json"].get("requires_shards"):
        # Provide dummy shards equal to threshold; server accepts count-based for now
        ms_user_id = results["ms_login_json"].get("user_id")
        verify = client.post("/api/auth/verify-shards", json={
            "user_id": ms_user_id,
            "shards": [{"dummy": 1}, {"dummy": 2}],
        })
        results["ms_verify_status_code"] = verify.status_code
        results["ms_verify_json"] = verify.get_json()
        if verify.status_code == 200:
            ms_token = results["ms_verify_json"].get("access_token")

    if ms_token:
        resp = client.get("/api/wallet/balance", headers={
            "Authorization": f"Bearer {ms_token}"
        })
        results["ms_wallet_balance_status_code"] = resp.status_code
        results["ms_wallet_balance_json"] = resp.get_json()
    else:
        results["ms_wallet_balance_status_code"] = None
        results["ms_wallet_balance_json"] = None

print(results)
