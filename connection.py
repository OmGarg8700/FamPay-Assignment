import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import redis
from dotenv import load_dotenv

from model import Base

load_dotenv()

MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# MySQL connection setup
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("MySQL connection successful.")
except Exception as e:
    print(f"[ERROR] connecting to MySQL: {e}")
    engine = None
    SessionLocal = None

# Redis connection setup
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    redis_client.ping()
    print("Redis connection successful.")
except Exception as e:
    print(f"[ERROR] connecting to Redis: {e}")
    redis_client = None


def init_db():
    if engine:
        Base.metadata.create_all(bind=engine)
    else:
        print("Skipping DB initialization due to failed connection.")
