# core/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.redis import redis_client
from app.models.user import User
from sqlmodel import Session, select
from passlib.context import CryptContext



oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash from a plain password."""
    return pwd_context.hash(password)


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Lưu token vào Redis
    redis_client.setex(
        f"token:{encoded_jwt}",
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        str(subject)
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        # Kiểm tra token trong Redis
        stored_user_id = redis_client.get(f"token:{token}")
        if not stored_user_id or stored_user_id != user_id:
            return None

        return user_id
    except JWTError:
        return None


async def get_current_user(
        session: Session,
        token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(token)
    if not user_id:
        raise credentials_exception

    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user


def create_refresh_token(subject: str) -> str:
    """Create a refresh token."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.REFRESH_TOKEN_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    # Lưu refresh token vào Redis
    redis_client.setex(
        f"refresh_token:{encoded_jwt}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        str(subject)
    )

    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[str]:
    """Verify a refresh token."""
    try:
        payload = jwt.decode(
            token,
            settings.REFRESH_TOKEN_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            return None

        # Kiểm tra token trong Redis
        stored_user_id = redis_client.get(f"refresh_token:{token}")
        if not stored_user_id or stored_user_id != user_id:
            return None

        return user_id
    except JWTError:
        return None


def revoke_all_tokens(user_id: str):
    """Revoke all tokens (access and refresh) for a user."""
    # Tìm và xóa tất cả tokens của user
    pattern = f"*:{user_id}"
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)
