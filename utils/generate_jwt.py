"""
Helper module for work with JWT token.
"""
from datetime import timedelta
import os
from typing import Optional
from jose import jwt, JWTError
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Helper function for generating JWT token from user's data.
    """
    to_encode = data.copy()
    print("SECRET_KEY", SECRET_KEY)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """
    Helper function for decoding JWT token and obtaining user's data from it.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise Exception("Token is invalid or has expired") from e
