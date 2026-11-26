"""Configuration — paths and MySQL credentials loaded from .env."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project paths
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
SQL_DIR = ROOT_DIR / "sql"

# Load environment variables from .env
load_dotenv(ROOT_DIR / ".env")

# MySQL settings
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "retail_sales")

# SQLAlchemy connection strings
MYSQL_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
MYSQL_URL_NO_DB = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/"
)

# Pipeline settings
SAMPLE_FRACTION = 1.0   # set to 0.1 for faster dev runs
SYNTHETIC_START_DATE = "2024-01-01"

# Forecasting settings
FORECAST_HORIZON = 14
TRAIN_FRACTION = 0.8
