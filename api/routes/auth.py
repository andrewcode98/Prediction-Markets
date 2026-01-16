from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth.service import register_user, authenticate_user

router = APIRouter(prefix="/auth", tags = ["auth"])

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(req: RegisterRequest):
    try:
        user = register_user(req.username, req.password)
        return {"user_id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail= str(e))

@router.post("/login")
def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail = "Invalid credentials")
    
    return {"user_id": user.id}