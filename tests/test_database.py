"""
RetailPulse — Tests: Database Connection
NOTE: Tests that require a live MySQL instance are marked BLOCKED.
      They will be skipped automatically if MySQL is not reachable.
      Run the full pipeline and configure .env before running these tests.
"""

import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ── Helper to check MySQL availability ────────────────────────────────────────
def mysql_available() -> bool:
    try:
        from src.database import test_connection
        return test_connection()
    except Exception:
        return False


MYSQL_SKIP = pytest.mark.skipif(
    not mysql_available(),
    reason="BLOCKED: MySQL not reachable. Configure .env and run python -m src.pipeline first."
)


# ── Tests that do NOT require MySQL ──────────────────────────────────────────

def test_config_has_database_name():
    from src.config import MYSQL_DATABASE
    assert isinstance(MYSQL_DATABASE, str)
    assert len(MYSQL_DATABASE) > 0


def test_config_has_host():
    from src.config import MYSQL_HOST
    assert isinstance(MYSQL_HOST, str)


def test_config_port_is_int():
    from src.config import MYSQL_PORT
    assert isinstance(MYSQL_PORT, int)
    assert MYSQL_PORT == 3306


def test_import_database_module():
    """The database module should import without error even if MySQL is offline."""
    from src import database
    assert hasattr(database, "test_connection")
    assert hasattr(database, "get_connection")
    assert hasattr(database, "query_to_df")


# ── Tests that REQUIRE MySQL ──────────────────────────────────────────────────

@MYSQL_SKIP
def test_connection_succeeds():
    from src.database import test_connection
    assert test_connection() is True


@MYSQL_SKIP
def test_database_exists():
    from src.database import query_to_df
    result = query_to_df("SELECT DATABASE() AS db")
    assert len(result) > 0


@MYSQL_SKIP
def test_fact_sales_has_rows():
    from src.database import query_to_df
    result = query_to_df("SELECT COUNT(*) AS cnt FROM fact_sales")
    assert result["cnt"].iloc[0] > 0


@MYSQL_SKIP
def test_fact_sales_no_negative_sales():
    from src.database import query_to_df
    result = query_to_df(
        "SELECT COUNT(*) AS cnt FROM fact_sales WHERE sales_amount <= 0"
    )
    assert result["cnt"].iloc[0] == 0


@MYSQL_SKIP
def test_dim_product_has_rows():
    from src.database import query_to_df
    result = query_to_df("SELECT COUNT(*) AS cnt FROM dim_product")
    assert result["cnt"].iloc[0] > 0


@MYSQL_SKIP
def test_all_tables_exist():
    from src.database import query_to_df
    from src.config import MYSQL_DATABASE
    result = query_to_df(
        f"SELECT TABLE_NAME FROM information_schema.TABLES "
        f"WHERE TABLE_SCHEMA = '{MYSQL_DATABASE}'"
    )
    expected_tables = {"fact_sales", "dim_product", "dim_location", "dim_date"}
    found_tables = set(result["TABLE_NAME"].tolist())
    assert expected_tables.issubset(found_tables), \
        f"Missing tables: {expected_tables - found_tables}"


@MYSQL_SKIP
def test_total_sales_matches_csv():
    """BLOCKED: Reconcile MySQL total sales against processed CSV total."""
    from src.database import query_to_df
    from src.data_loader import load_processed
    db_total = query_to_df(
        "SELECT ROUND(SUM(sales_amount), 2) AS total FROM fact_sales"
    )["total"].iloc[0]
    csv_total = round(load_processed()["sales_amount"].sum(), 2)
    assert abs(float(db_total) - float(csv_total)) < 100.0, \
        f"DB total ({db_total}) vs CSV total ({csv_total}) differ by > ₹100"
