# signup.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from authentication.hashing_func import hash_password
from app.api.v1.endpoints.router import get_db, users_table

router = APIRouter(prefix="/signup", tags=["Signup"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str

@router.post("/")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    query = select(users_table).where(users_table.c.email == user.email)
    result = db.execute(query).fetchone()

    if result:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = hash_password(user.password)
    insert_stmt = insert(users_table).values(email=user.email, hashed_password=hashed_pw)
    db.execute(insert_stmt)
    db.commit()
    return {"message": "User registered successfully"}


@router.post("/signup/oauth/{provider}")
def oauth_signup(provider: str, db: Session = Depends(get_db)):
    fake_email = f"user_{provider}@example.com"
    query = select(users_table).where(users_table.c.email == fake_email)
    existing_user = db.execute(query).fetchone()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered via OAuth")

    hashed_pw = hash_password(fake_email + "_oauth")
    insert_stmt = insert(users_table).values(email=fake_email, hashed_password=hashed_pw)
    db.execute(insert_stmt)
    db.commit()

    return {"message": f"{provider.capitalize()} OAuth signup successful"}
