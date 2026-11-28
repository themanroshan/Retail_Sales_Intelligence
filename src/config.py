"""
RetailPulse — Configuration
Loads paths and MySQL credentials from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Project paths ─────────────────────────────────────────────────────────────
ROOT_DIR       = Path(__file__).resolve().parents[1]
DATA_RAW       = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
DATA_SAMPLE    = ROOT_DIR / "data" / "sample"
SQL_DIR        = ROOT_DIR / "sql"
REPORTS_DIR    = ROOT_DIR / "reports"
EXCEL_DIR      = ROOT_DIR / "excel"

# ── Load .env ─────────────────────────────────────────────────────────────────
load_dotenv(ROOT_DIR / ".env")

# ── MySQL settings ────────────────────────────────────────────────────────────
MYSQL_HOST     = os.getenv("MYSQL_HOST",     "localhost")
MYSQL_PORT     = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER     = os.getenv("MYSQL_USER",     "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "retailpulse")

# ── Data source toggle ────────────────────────────────────────────────────────
# Set DATA_SOURCE=csv in .env to run dashboard without MySQL
DATA_SOURCE    = os.getenv("DATA_SOURCE", "csv")     # "mysql" or "csv"

# ── Raw data filename (actual Kaggle file or synthetic) ───────────────────────
RAW_FILENAME   = "retailpulse_transactions.csv"
RAW_FILE_PATH  = DATA_RAW / RAW_FILENAME

PROCESSED_FILE = DATA_PROCESSED / "retailpulse_clean.csv"
SAMPLE_FILE    = DATA_SAMPLE    / "retailpulse_sample.csv"

# ── Synthetic data settings ───────────────────────────────────────────────────
SYNTHETIC_SEED       = 42
SYNTHETIC_N_ROWS     = 10_000
SYNTHETIC_START_DATE = "2022-01-01"
SYNTHETIC_END_DATE   = "2024-12-31"
