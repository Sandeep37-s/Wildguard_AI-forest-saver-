"""
app.py - FastAPI backend for Police Security Bot
- Provides /login and /get_messages endpoints
- Uses MySQL (telegram_dashboard) via SQLAlchemy core
- Auth with JWT + HttpOnly cookie (and Bearer fallback)
- Passwords verified with bcrypt (passlib)
- Basic in-memory rate limiting for login attempts
- Renders HTML UI (index.html, login.html, dashboard.html)
"""
from pathlib import Path
import os
import time
import json
from typing import Optional, Dict

from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, select, func
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv

# ---------------------------------------------------------
# 1. Initialize FastAPI
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Police Security Bot API")

# Serve static files (CSS, JS, Images)
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

# Setup Jinja2 templates for HTML UI
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/dashboard.html", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ---------------------------------------------------------
# 2. Load environment variables
# ---------------------------------------------------------
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "telegram_dashboard")
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_to_a_very_long_random_secret")
JWT_ALG = "HS256"
ACCESS_EXPIRE_SECONDS = int(os.getenv("ACCESS_EXPIRE_SECONDS", "3600"))

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"

# ---------------------------------------------------------
# 3. Database setup (SQLAlchemy)
# ---------------------------------------------------------
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
metadata = MetaData()
metadata.reflect(bind=engine)

messages = metadata.tables.get("messages")
admins = metadata.tables.get("admins")

if messages is None or admins is None:
    raise RuntimeError("Error: Missing 'messages' or 'admins' tables in your database.")

# ---------------------------------------------------------
# 4. Security utilities
# ---------------------------------------------------------
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_ctx.verify(plain, hashed)
    except Exception:
        return False

def create_access_token(subject: str, expires_in: int = ACCESS_EXPIRE_SECONDS):
    payload = {"sub": subject, "exp": int(time.time()) + expires_in}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        return None

# ---------------------------------------------------------
# 5. Rate limiting
# ---------------------------------------------------------
_login_failures: Dict[str, list] = {}
_blocked_until: Dict[str, float] = {}
MAX_FAILED = 5
LOCK_WINDOW = 300
LOCK_TIME = 600

def record_failed_attempt(ip: str):
    now = time.time()
    arr = _login_failures.setdefault(ip, [])
    arr.append(now)
    _login_failures[ip] = [t for t in arr if t > now - LOCK_WINDOW]

def failed_attempts_recent(ip: str) -> int:
    now = time.time()
    return len([t for t in _login_failures.get(ip, []) if t > now - LOCK_WINDOW])

def is_blocked(ip: str) -> bool:
    return time.time() < _blocked_until.get(ip, 0)

def block_ip(ip: str):
    _blocked_until[ip] = time.time() + LOCK_TIME
    _login_failures.pop(ip, None)

# ---------------------------------------------------------
# 6. CORS setup
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost/security-bot",
        "file://",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 7. Pydantic models
# ---------------------------------------------------------
class LoginIn(BaseModel):
    username: str
    password: str

# ---------------------------------------------------------
# 8. Auth dependency
# ---------------------------------------------------------
def get_current_admin(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        admin_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    with engine.connect() as conn:
        row = conn.execute(
            select(admins.c.id, admins.c.username).where(admins.c.id == admin_id)
        ).fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Admin not found")

    return {"id": admin_id, "username": row.username}

# ---------------------------------------------------------
# 9. HTML Routes (UI pages)
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ---------------------------------------------------------
# 10. API Routes (JSON)
# ---------------------------------------------------------
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    return JSONResponse({"status": "ok"})

@app.post("/login")
def login(payload: LoginIn, request: Request, response: Response):
    ip = request.client.host if request.client else "unknown"
    if is_blocked(ip):
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try later.")

    with engine.connect() as conn:
        row = conn.execute(
            select(admins.c.id, admins.c.password_hash).where(admins.c.username == payload.username)
        ).fetchone()

    if not row or not verify_password(payload.password, row.password_hash):
        record_failed_attempt(ip)
        if failed_attempts_recent(ip) >= MAX_FAILED:
            block_ip(ip)
            raise HTTPException(status_code=429, detail="Account temporarily locked.")
        return JSONResponse({"success": False, "message": "Invalid username or password"}, status_code=401)


    token = create_access_token(subject=str(row.id))
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="Lax",
        secure=False,
        max_age=ACCESS_EXPIRE_SECONDS
    )
    return {"success": True, "message": "Logged in"}

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True}

@app.get("/get_messages")
def get_messages(label: str = None, admin=Depends(get_current_admin)):
    with engine.connect() as conn:
        # ---- counts ----
        total = conn.execute(
            select(func.count()).select_from(messages)
        ).scalar() or 0

        suspicious = conn.execute(
            select(func.count())
            .select_from(messages)
            .where(messages.c.label == "suspicious")
        ).scalar() or 0

        safe = conn.execute(
            select(func.count())
            .select_from(messages)
            .where(messages.c.label == "safe")
        ).scalar() or 0

        # ---- base query ----
        base_query = select(
            messages.c.id,
            messages.c.chat_id,
            messages.c.username,
            messages.c.text,
            messages.c.created_at,
            messages.c.label
        )

        # ---- apply filter if clicked ----
        if label:
            base_query = base_query.where(messages.c.label == label)

        rows = conn.execute(
            base_query.order_by(messages.c.id.desc()).limit(50)
        ).fetchall()

    msgs = []
    for r in rows:
        msgs.append({
            "id": int(r.id),
            "sender": r.username,
            "text": r.text,
            "label": r.label,
            "timestamp": str(r.created_at),
        })

    return {
        "stats": {
            "total": total,
            "suspicious": suspicious,
            "safe": safe
        },
        "messages": msgs
    }


@app.get("/health")
def health():
    return {"status": "ok"}
