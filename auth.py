import os
import time
import bcrypt
import jwt
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest

USERNAME = os.getenv("APP_USERNAME")
PASSWORD_HASH = os.getenv("APP_PASSWORD_HASH")
JWT_SECRET = os.getenv("APP_JWT_SECRET")
SESSION_TIMEOUT = 600  # 10 minutes

security = HTTPBasic()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_jwt(username: str) -> str:
    payload = {
        "sub": username,
        "exp": int(time.time()) + SESSION_TIMEOUT
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired, please login again")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if not compare_digest(username, USERNAME):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not verify_password(password, PASSWORD_HASH):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_jwt(username)
    return token

def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    username = decode_jwt(token)
    return username

router = APIRouter()

@router.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    token = authenticate(credentials)
    return {"token": token, "expires_in": SESSION_TIMEOUT}
