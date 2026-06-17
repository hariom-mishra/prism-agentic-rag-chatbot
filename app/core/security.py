import bcrypt
import joserfc.jwt
import joserfc.jwk
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
    key = joserfc.jwk.import_key(setting.SECRET_KEY, "oct")
    return joserfc.jwt.encode(header, payload, key)

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
    key = joserfc.jwk.import_key(setting.SECRET_KEY, "oct")
    return joserfc.jwt.encode(header, payload, key)

def verify_password(password: str, hashed_password: str) -> bool:
    try: 
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def decode_access_token(token: str) -> dict:
    try:
        key = joserfc.jwk.import_key(setting.SECRET_KEY, "oct")
        decoded = joserfc.jwt.decode(token, key)
        return dict(decoded.claims)
    except Exception:
        return None