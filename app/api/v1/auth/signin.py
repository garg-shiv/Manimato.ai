# signin.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from authentication.hashing_func import verify_password
from app.api.v1.endpoints.router import get_db, users_table

router = APIRouter(prefix="/signin", tags=["Signin"])

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    query = select(users_table).where(users_table.c.email == user.email)
    db_user = db.execute(query).fetchone()

    if not db_user:
        raise HTTPException(status_code=404, detail="Email not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"message": "Login successful"}


@router.get("/login/oauth/{provider}")
def oauth_login(provider: str, db: Session = Depends(get_db)):
    fake_email = f"user_{provider}@example.com"
    query = select(users_table).where(users_table.c.email == fake_email)
    user = db.execute(query).fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not registered via OAuth")

    return {"message": f"{provider.capitalize()} OAuth login successful"}
