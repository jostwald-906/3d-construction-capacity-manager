from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import User

client = TestClient(app)

def test_login_and_me_flow():
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.username=="tester").first()
        if not u:
            u = User(username="tester", password_hash=hash_password("pass"), role="admin")
            db.add(u); db.commit()
        resp = client.post("/auth/login", data={"username":"tester","password":"pass"})
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "tester"
    finally:
        db.close()
