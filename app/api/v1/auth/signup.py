# signup.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.utils.hashing_function import hash_password
from app.database.models.user import User
from app.database.session import get_db

router = APIRouter(prefix="/signup", tags=["Signup"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

@router.post("/")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
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
    existing_user = db.query(User).filter(User.email == fake_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered via OAuth")
    hashed_pw = hash_password(fake_email + "_oauth")
    new_user = User(email=fake_email, hashed_password=hashed_pw, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"{provider.capitalize()} OAuth signup successful"}
