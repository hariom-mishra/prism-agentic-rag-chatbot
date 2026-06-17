import sys
import os

# Add both the root directory and 'app' directory to sys.path to resolve core.* and app.core.* imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token
)

class MockUser:
    def __init__(self, user_id, role):
        self.id = user_id
        self.role = role

def test_password_hashing_and_verification():
    password = "MySuperSecretPassword123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_create_and_decode_access_token():
    user = MockUser(user_id=42, role="admin")
    token = create_access_token(user)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "42"
    assert decoded.get("role") == "admin"

def test_create_refresh_token():
    user = MockUser(user_id=123, role="user")
    token = create_refresh_token(user)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "123"
    assert decoded.get("role") == "user"
    assert decoded.get("refresh") is True

def test_decode_invalid_token():
    assert decode_access_token("invalid_token") is None
