
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ==========================================================
# SQL SERVER CONNECTION
# ==========================================================

SERVER = "SAGEPAC-LTD"
DATABASE = "HealthcareAnalytics"
DRIVER = "ODBC Driver 18 for SQL Server"

connection_string = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

connection_url = quote_plus(connection_string)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={connection_url}",
    fast_executemany=True
)

print("Loading Related Tables to SQL Server")
print("=" * 60)


# ==========================================================
# TEST CONNECTION
# ==========================================================

with engine.connect() as connection:
    database_name = connection.execute(
        text("SELECT DB_NAME()")
    ).scalar()

print(f"\nConnected to: {database_name}")


# ==========================================================
# LOAD PROCESSED FILES
# ==========================================================

print("\nLoading processed CSV files...")

conditions = pd.read_csv(
    PROCESSED_DIR / "conditions_clean.csv"
)

procedures = pd.read_csv(
    PROCESSED_DIR / "procedures_clean.csv"
)

providers = pd.read_csv(
    PROCESSED_DIR / "providers_clean.csv"
)

organizations = pd.read_csv(
    PROCESSED_DIR / "organizations_clean.csv"
)

print(f"Conditions:    {len(conditions):,}")
print(f"Procedures:    {len(procedures):,}")
print(f"Providers:     {len(providers):,}")
print(f"Organizations: {len(organizations):,}")


# ==========================================================
# WRITE TO SQL SERVER
# ==========================================================

tables = {
    "conditions": conditions,
    "procedures": procedures,
    "providers": providers,
    "organizations": organizations
}

print("\nWriting tables to SQL Server...")

for table_name, dataframe in tables.items():

    dataframe.to_sql(
        name=table_name,
        con=engine,
        schema="dbo",
        if_exists="replace",
        index=False,
        chunksize=1000
    )

    print(f"SUCCESS: dbo.{table_name}")


# ==========================================================
# VERIFY SQL ROW COUNTS
# ==========================================================

print("\nVerifying SQL Server row counts...")

with engine.connect() as connection:

    for table_name in tables:

        query = text(
            f"SELECT COUNT(*) FROM dbo.{table_name}"
        )

        count = connection.execute(query).scalar()

        print(f"{table_name}: {count:,} rows")


print("\nSUCCESS")
print("=" * 60)
print("All related healthcare tables loaded into SQL Server.")