import bcrypt
from authlib.jose import jwt
from datetime import datetime, timezone, timedelta
from core.config import setting

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(user) -> str:
    expires = datetime.now(timezone.utc) + timedelta(seconds=setting.TOKEN_EXP)
    header = {"alg": setting.ALGORITHM}
    payload = {
        "exp": int(expires.timestamp()),
        "sub": str(user.id),
        "role": user.role
    }
    return jwt.encode(header, payload, setting.SECRET_KEY).decode("utf-8")

def create_refresh_token(user) -> str:
    # Refresh token expires in 7 days
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    header = {"alg": setting.ALGORITHM}
    payload = {
        "exp": int(expires.timestamp()),
        "sub": str(user.id),
        "role": user.role,
        "refresh": True
    }
    return jwt.encode(header, payload, setting.SECRET_KEY).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    try: 
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False