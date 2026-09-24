
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# ==========================================================
# PROJECT PATHS
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

print("Healthcare Operations Analytics - SQL Server Loader")
print("=" * 60)

# ==========================================================
# TEST CONNECTION
# ==========================================================

print("\nTesting SQL Server connection...")

try:
    with engine.connect() as connection:
        server_name = connection.execute(
            text("SELECT @@SERVERNAME")
        ).scalar()

        database_name = connection.execute(
            text("SELECT DB_NAME()")
        ).scalar()

    print("Connection successful.")
    print(f"Server:   {server_name}")
    print(f"Database: {database_name}")

except Exception as error:
    print("\nCONNECTION FAILED")
    print(error)
    raise SystemExit


# ==========================================================
# LOAD PROCESSED DATA
# ==========================================================

print("\nLoading processed CSV files...")

patients = pd.read_csv(
    PROCESSED_DIR / "patients_clean.csv"
)

encounters = pd.read_csv(
    PROCESSED_DIR / "encounters_clean.csv"
)

patient_encounters = pd.read_csv(
    PROCESSED_DIR / "patient_encounters.csv"
)

print(f"Patients loaded:           {len(patients):,}")
print(f"Encounters loaded:         {len(encounters):,}")
print(f"Patient encounters loaded: {len(patient_encounters):,}")


# ==========================================================
# WRITE TABLES TO SQL SERVER
# ==========================================================

print("\nWriting tables to SQL Server...")

patients.to_sql(
    name="patients",
    con=engine,
    schema="dbo",
    if_exists="replace",
    index=False,
    chunksize=1000
)

print("SUCCESS: dbo.patients")

encounters.to_sql(
    name="encounters",
    con=engine,
    schema="dbo",
    if_exists="replace",
    index=False,
    chunksize=1000
)

print("SUCCESS: dbo.encounters")

patient_encounters.to_sql(
    name="patient_encounters",
    con=engine,
    schema="dbo",
    if_exists="replace",
    index=False,
    chunksize=1000
)

print("SUCCESS: dbo.patient_encounters")


# ==========================================================
# VERIFY SQL SERVER ROW COUNTS
# ==========================================================

print("\nVerifying SQL Server tables...")

verification_queries = {
    "patients": "SELECT COUNT(*) FROM dbo.patients",
    "encounters": "SELECT COUNT(*) FROM dbo.encounters",
    "patient_encounters": "SELECT COUNT(*) FROM dbo.patient_encounters"
}

with engine.connect() as connection:

    for table_name, query in verification_queries.items():

        count = connection.execute(
            text(query)
        ).scalar()

        print(f"{table_name}: {count:,} rows")


# ==========================================================
# FINAL MESSAGE
# ==========================================================

print("\nSUCCESS")
print("=" * 60)
print("Processed healthcare data loaded into SQL Server.")
print(f"Database: {DATABASE}")