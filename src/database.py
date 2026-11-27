"""
RetailPulse — Database Layer
=============================
Uses mysql-connector-python (no SQLAlchemy).
All credentials are read from environment variables via src.config.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import mysql.connector
from mysql.connector import Error
import pandas as pd

from src.config import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER,
    MYSQL_PASSWORD, MYSQL_DATABASE
)


# ── Connection helpers ────────────────────────────────────────────────────────

def get_connection(database: str | None = None):
    """
    Open and return a mysql.connector connection.
    If database is None, connects without selecting a database (used for CREATE DATABASE).
    """
    kwargs = dict(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
    )
    if database:
        kwargs["database"] = database

    try:
        conn = mysql.connector.connect(**kwargs)
        return conn
    except Error as e:
        raise ConnectionError(
            f"Cannot connect to MySQL at {MYSQL_HOST}:{MYSQL_PORT} "
            f"as user '{MYSQL_USER}'.\n"
            f"MySQL error: {e}\n\n"
            "Check your .env file and ensure MySQL Server is running."
        ) from e


def test_connection() -> bool:
    """Return True if MySQL is reachable, False otherwise."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False


# ── Schema management ─────────────────────────────────────────────────────────

def create_database() -> None:
    """Create the retailpulse database if it does not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[database] Database '{MYSQL_DATABASE}' is ready.")


def _run_sql_file(sql_path: Path) -> None:
    """Execute a multi-statement SQL file against the target database."""
    sql_text = sql_path.read_text(encoding="utf-8")
    conn = get_connection(database=MYSQL_DATABASE)
    cursor = conn.cursor()
    for statement in sql_text.split(";"):
        stmt = statement.strip()
        if stmt and not stmt.startswith("--"):
            cursor.execute(stmt)
    conn.commit()
    cursor.close()
    conn.close()


def create_tables(sql_dir: Path = None) -> None:
    """Create all tables by running sql/02_create_tables.sql."""
    if sql_dir is None:
        sql_dir = ROOT / "sql"
    sql_path = sql_dir / "02_create_tables.sql"
    _run_sql_file(sql_path)
    print("[database] Tables created.")


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_dataframe(df: pd.DataFrame, table: str, batch_size: int = 1000) -> int:
    """
    Insert a DataFrame into a MySQL table using executemany.
    Uses INSERT IGNORE to avoid duplicating rows on re-run.
    Returns the number of rows inserted.
    """
    if df.empty:
        print(f"[database] {table}: DataFrame is empty, nothing to insert.")
        return 0

    # Replace NaN with None for MySQL NULL
    df_clean = df.where(pd.notna(df), other=None)
    cols    = list(df_clean.columns)
    placeholders = ", ".join(["%s"] * len(cols))
    col_list     = ", ".join([f"`{c}`" for c in cols])
    sql          = f"INSERT IGNORE INTO `{table}` ({col_list}) VALUES ({placeholders})"

    conn   = get_connection(database=MYSQL_DATABASE)
    cursor = conn.cursor()
    rows   = [tuple(row) for row in df_clean.itertuples(index=False, name=None)]
    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        cursor.executemany(sql, batch)
        inserted += cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[database] {table}: {inserted:,} rows inserted (INSERT IGNORE).")
    return inserted


def load_dim_product(df: pd.DataFrame) -> int:
    return _load_dataframe(df, "dim_product")


def load_dim_location(df: pd.DataFrame) -> int:
    return _load_dataframe(df, "dim_location")


def load_dim_date(df: pd.DataFrame) -> int:
    return _load_dataframe(df, "dim_date")


def load_fact_sales(df: pd.DataFrame) -> int:
    return _load_dataframe(df, "fact_sales")


# ── Query helpers ─────────────────────────────────────────────────────────────

def query_to_df(sql: str) -> pd.DataFrame:
    """Run a SELECT query and return the results as a DataFrame."""
    conn = get_connection(database=MYSQL_DATABASE)
    try:
        df = pd.read_sql(sql, conn)
    finally:
        conn.close()
    return df
