import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import redis
from dotenv import load_dotenv
from model import Base

load_dotenv()

# MySQL config from .env
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")  # default to docker service name
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Redis config
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# MySQL connection setup
engine = None
SessionLocal = None
MAX_RETRIES = 10

for i in range(MAX_RETRIES):
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ MySQL connection successful.")
        break
    except Exception as e:
        print(f"[WAIT] MySQL not ready yet ({i+1}/{MAX_RETRIES}): {e}")
        time.sleep(2)
else:
    print("[ERROR] MySQL connection failed after retries.")
    engine = None
    SessionLocal = None

# Redis connection setup
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    redis_client.ping()
    print("✅ Redis connection successful.")
except Exception as e:
    print(f"[ERROR] connecting to Redis: {e}")
    redis_client = None


def init_db():
    if engine:
        Base.metadata.create_all(bind=engine)
    else:
        print("⚠️ Skipping DB initialization due to failed MySQL connection.")
