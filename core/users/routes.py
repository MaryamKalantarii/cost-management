from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.users.schemas import UserRegisterSchema, UserLoginSchema
from core.users.models import UserModel
from core.core.database import get_db
from core.auth.jwt_auth import generate_access_token, generate_refresh_token, decode_refresh_token

router = APIRouter(prefix="/users", tags=["Users"])


# ------------------ REGISTER ------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def user_register(request: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    ✅ Register a new user.
    - Checks if username already exists.
    - Hashes the password before saving.
    - Stores the user in the database.
    """
    
    
    if db.query(UserModel).filter_by(username=request.username.lower()).first():
        raise HTTPException(status_code=409, detail="Username already exists")

    user = UserModel(username=request.username.lower())
    user.set_password(request.password)
    db.add(user)
    db.commit()
    return {"detail": "User registered successfully"}


# ------------------ LOGIN ------------------
@router.post("/login")
async def user_login(request: UserLoginSchema, response: Response, db: Session = Depends(get_db)):
    """
    ✅ User login and token generation.
    - Verifies username and password.
    - Generates an access token (short-lived) and refresh token (long-lived).
    - Stores tokens in secure HttpOnly cookies.
    """
    
    
    user = db.query(UserModel).filter_by(username=request.username.lower()).first()
    if not user or not user.verify_password(request.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)

    # Set HttpOnly Cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # 🔒 in production: True
        samesite="strict",
        max_age=60 * 5,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=3600 * 24,
    )

    return JSONResponse(
        content={
            "detail": "logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


# ------------------ REFRESH TOKEN ------------------
@router.post("/refresh-token")
async def refresh_access_token(request: Request, response: Response):
    """
    🔄 Refresh access token.
    - Reads refresh token from HttpOnly cookie.
    - Validates it.
    - Generates a new access token and updates the cookie.
    - No need for user to log in again.
    """
    
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    user_id = decode_refresh_token(refresh_token)
    new_access_token = generate_access_token(user_id)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,  # 🔒 set True in production
        samesite="strict",
        max_age=60 * 5,
    )
    return {"detail": "Access token refreshed"}


# ------------------ LOGOUT ------------------
@router.post("/logout")
async def logout(response: Response):
    """
    🚪 Logout user.
    - Deletes both access_token and refresh_token cookies.
    - Ends the user's session securely.
    """
    
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Logged out successfully"}
