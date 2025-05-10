import sqlalchemy
from app.database import metadata

users = sqlalchemy.Table(
    "auth_users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True, index=True, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String, unique=True, index=True, nullable=False),
)

revoked_tokens = sqlalchemy.Table(
    "revoked_tokens", metadata,
    sqlalchemy.Column("jti", sqlalchemy.String, primary_key=True),
)
