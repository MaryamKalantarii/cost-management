from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError
from users.models import UserModel
from core.database import get_db
from core.config import settings

# HTTP Bearer scheme (reads Authorization: Bearer <token>)
security = HTTPBearer(auto_error=False)


# ------------------ AUTHENTICATION DEPENDENCY ------------------
def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Validates an incoming JWT Access Token from Authorization header.

    Steps:
    1. Extract token from the `Authorization` header.
    2. Decode and verify JWT signature using the secret key.
    3. Check token type and expiration time.
    4. Fetch and return the user from the database.

    Raises:
    - 401 if token is missing, invalid, expired, or signature is incorrect.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not provided",
        )

    token = credentials.credentials
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

        # Token validation checks
        user_id = decoded.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        if decoded.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if datetime.now(timezone.utc) > datetime.fromtimestamp(decoded.get("exp"), tz=timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")

        # Fetch user from DB
        user = db.query(UserModel).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except (InvalidSignatureError, DecodeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {e}")


# ------------------ ACCESS TOKEN GENERATOR ------------------
def generate_access_token(user_id: int, expires_in: int = 60 * 5) -> str:
    """
    Generates a short-lived Access Token (default: 5 minutes).
    - Contains `type='access'` and `user_id`.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "type": "access",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


# ------------------ REFRESH TOKEN GENERATOR ------------------
def generate_refresh_token(user_id: int, expires_in: int = 3600 * 24) -> str:
    """
    Generates a long-lived Refresh Token (default: 24 hours).
    - Used to issue a new Access Token without re-login.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "type": "refresh",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


# ------------------ REFRESH TOKEN DECODER ------------------
def decode_refresh_token(token: str) -> int:
    """
    Decodes and validates a Refresh Token.

    Steps:
    1. Decodes JWT and validates signature.
    2. Checks token type and expiration.
    3. Returns `user_id` if valid.

    Raises:
    - 401 for invalid/expired/malformed tokens.
    """
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

        # Check claims
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if datetime.now(timezone.utc) > datetime.fromtimestamp(decoded.get("exp"), tz=timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")

        user_id = decoded.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID missing")

        return user_id

    except (InvalidSignatureError, DecodeError):
        raise HTTPException(status_code=401, detail="Invalid token signature")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token decode failed: {e}")
