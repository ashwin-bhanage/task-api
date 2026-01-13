from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECERT_KEY = "3e3771322ca9e1cdf52d0791e427fdaa80d21d814ef208ab77a0bfe2ef5469ad"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7           #for 7days

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password_hash: str) -> str:
    """
    Hash password
    """
    return pwd_context.hash(password_hash)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECERT_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECERT_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
