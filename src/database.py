"""MySQL connection and schema helpers."""

from sqlalchemy import create_engine, text
from src.config import MYSQL_URL, MYSQL_URL_NO_DB, MYSQL_DATABASE, SQL_DIR


def get_engine(with_db: bool = True):
    """Return a SQLAlchemy engine for MySQL."""
    url = MYSQL_URL if with_db else MYSQL_URL_NO_DB
    return create_engine(url)


def create_database():
    """Create the retail_sales database if it doesn't exist."""
    engine = get_engine(with_db=False)
    with engine.connect() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
        conn.commit()
    print(f"Database '{MYSQL_DATABASE}' is ready.")


def create_tables():
    """Run sql/schema.sql to create all tables."""
    schema_file = SQL_DIR / "schema.sql"
    sql_text = schema_file.read_text(encoding="utf-8")

    engine = get_engine()
    with engine.begin() as conn:
        for statement in sql_text.split(";"):
            if statement.strip():
                conn.execute(text(statement))
    print("Tables created from schema.sql")


def load_dataframe(df, table_name: str):
    """Bulk-insert a DataFrame into a MySQL table."""
    engine = get_engine()
    df.to_sql(table_name, con=engine, if_exists="append", index=False, chunksize=5000)
    print(f"Loaded {len(df):,} rows into {table_name}")
