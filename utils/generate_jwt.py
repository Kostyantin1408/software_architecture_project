from datetime import timedelta
import os
from typing import Optional
from jose import jwt


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
