import os
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_env_path)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://user:password@127.0.0.1:3306/namis_yogur",
)
