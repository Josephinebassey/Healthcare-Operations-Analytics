
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

files = [
    "conditions.csv",
    "procedures.csv",
    "providers.csv",
    "organizations.csv"
]

print("RELATED TABLE INSPECTION")
print("=" * 70)

for filename in files:

    path = RAW_DIR / filename
    df = pd.read_csv(path)

    print(f"\n{filename.upper()}")
    print("-" * 70)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nMissing values:")
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if len(missing) == 0:
        print("None")
    else:
        print(missing)

    print("\nFirst 3 rows:")
    print(df.head(3).to_string(index=False))

print("\n" + "=" * 70)
print("Inspection complete.")