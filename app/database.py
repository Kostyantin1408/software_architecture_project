import sqlalchemy
import databases
import os 

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    DATABASE_URL.replace("+aiosqlite", ""),
    connect_args={"check_same_thread": False}
)
