from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.session import get_db
from app.utils.hashing_function import hash_password, verify_password
from app.utils.jwt_helper import create_access_token, verify_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


oauth2_scheme = APIKeyHeader(name="Authorization")



SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# -----------------------------
# Models
# -----------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInDB(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = {
        "from_attributes": True
    }


# -----------------------------
# Helpers / Dependencies
# -----------------------------

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInDB.model_validate(user)




async def require_admin(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


# -----------------------------
# Signup Routes
# -----------------------------

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="User with this email already exists")
    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/signup/oauth/{provider}")
def oauth_signup(provider: str, db: Session = Depends(get_db)):
    fake_email = f"user_{provider}@example.com"
    if db.query(User).filter(User.email == fake_email).first():
        raise HTTPException(status_code=400, detail="User already registered via OAuth")
    hashed_pw = hash_password(fake_email + "_oauth")
    new_user = User(email=fake_email, hashed_password=hashed_pw, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"{provider.capitalize()} OAuth signup successful"}


# -----------------------------
# Signin Routes
# -----------------------------


@router.post("/signin", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    email = user.email.strip().lower()
    db_user = db.query(User).filter(User.email == email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Email not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token_expires = timedelta(minutes=30)
    token = create_access_token(
        {"sub": db_user.email, "user_id": db_user.id},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer"}



@router.get("/signin/oauth/{provider}")
def oauth_login(provider: str, db: Session = Depends(get_db)):
    fake_email = f"user_{provider}@example.com"
    user = db.query(User).filter(User.email == fake_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not registered via OAuth")
    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


# -----------------------------
# Protected Routes
# -----------------------------

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user


@router.get("/admin-only")
async def admin_only(current_user: UserInDB = Depends(require_admin)):
    return {"message": f"Welcome, admin {current_user.email}!"}
