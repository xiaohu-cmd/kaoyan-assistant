from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from backend.database import get_db
import sqlite3

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = "kaoyan-assistant-secret-key-2026-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except JWTError:
        raise credentials_exception
    cursor = db.execute("SELECT id, username, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user is None:
        raise credentials_exception
    return dict(user)

@router.post("/register", response_model=UserResponse)
def register(req: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    existing = db.execute("SELECT id FROM users WHERE username = ?", (req.username,)).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    password_hash = get_password_hash(req.password)
    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (req.username, password_hash)
    )
    user = db.execute("SELECT id, username, created_at FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(user)

@router.post("/login", response_model=TokenResponse)
def login(req: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    user = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (req.username,)).fetchone()
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user["id"])})
    return {"access_token": access_token, "token_type": "bearer"}


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=4, max_length=100)


@router.put("/password")
def change_password(
    req: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    user = db.execute("SELECT id, password_hash FROM users WHERE id = ?", (current_user["id"],)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(req.old_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    new_hash = get_password_hash(req.new_password)
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, current_user["id"]))
    return {"message": "Password changed successfully"}
