# signin.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.utils.hashing_function import verify_password
from app.database.models.user import User
from app.database.session import get_db
from app.utils.jwt_helper import create_access_token, verify_access_token

router = APIRouter(prefix="/signin", tags=["Signin"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin/")

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

# Dependency to get the current user from the JWT token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInDB(id=user.id, email=user.email, role=user.role)

# Dependency to require admin role
async def require_admin(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.post("/", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Email not found")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    token = create_access_token({"sub": db_user.email, "user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/login/oauth/{provider}")
def oauth_login(provider: str, db: Session = Depends(get_db)):
    fake_email = f"user_{provider}@example.com"
    user = db.query(User).filter(User.email == fake_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not registered via OAuth")
    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

# Example protected endpoint
@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user

# Example admin-only endpoint
@router.get("/admin-only")
async def admin_only(current_user: UserInDB = Depends(require_admin)):
    return {"message": f"Welcome, admin {current_user.email}!"}
