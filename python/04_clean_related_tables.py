
import pandas as pd
from pathlib import Path

# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Cleaning Related Healthcare Tables")
print("=" * 60)


# ==========================================================
# LOAD RAW DATA
# ==========================================================

conditions = pd.read_csv(RAW_DIR / "conditions.csv")
procedures = pd.read_csv(RAW_DIR / "procedures.csv")
providers = pd.read_csv(RAW_DIR / "providers.csv")
organizations = pd.read_csv(RAW_DIR / "organizations.csv")

print("\nRaw tables loaded.")
print(f"Conditions:    {len(conditions):,}")
print(f"Procedures:    {len(procedures):,}")
print(f"Providers:     {len(providers):,}")
print(f"Organizations: {len(organizations):,}")


# ==========================================================
# CONDITIONS
# ==========================================================

print("\nCleaning conditions...")

conditions_clean = conditions.copy()

conditions_clean["START"] = pd.to_datetime(
    conditions_clean["START"],
    errors="coerce"
)

conditions_clean["STOP"] = pd.to_datetime(
    conditions_clean["STOP"],
    errors="coerce"
)

conditions_clean = conditions_clean.rename(
    columns={
        "PATIENT": "PATIENT_ID",
        "ENCOUNTER": "ENCOUNTER_ID",
        "CODE": "CONDITION_CODE",
        "DESCRIPTION": "CONDITION_DESCRIPTION"
    }
)

# Whether a condition has no recorded stop date
conditions_clean["NO_RECORDED_STOP"] = (
    conditions_clean["STOP"].isna()
)

# ==========================================================
# PROCEDURES
# ==========================================================

print("Cleaning procedures...")

procedures_clean = procedures.copy()

procedures_clean["START"] = pd.to_datetime(
    procedures_clean["START"],
    errors="coerce",
    utc=True
)

procedures_clean["STOP"] = pd.to_datetime(
    procedures_clean["STOP"],
    errors="coerce",
    utc=True
)

procedures_clean = procedures_clean.rename(
    columns={
        "PATIENT": "PATIENT_ID",
        "ENCOUNTER": "ENCOUNTER_ID",
        "CODE": "PROCEDURE_CODE",
        "DESCRIPTION": "PROCEDURE_DESCRIPTION",
        "REASONCODE": "REASON_CODE",
        "REASONDESCRIPTION": "REASON_DESCRIPTION"
    }
)

procedures_clean["PROCEDURE_DURATION_MIN"] = (
    procedures_clean["STOP"] -
    procedures_clean["START"]
).dt.total_seconds() / 60

procedures_clean["BASE_COST"] = pd.to_numeric(
    procedures_clean["BASE_COST"],
    errors="coerce"
)


# ==========================================================
# PROVIDERS
# ==========================================================

print("Cleaning providers...")

# Keep analytical fields while removing unnecessary
# provider names, street addresses, NPI and coordinates.

provider_columns = [
    "Id",
    "ORGANIZATION",
    "GENDER",
    "SPECIALITY",
    "CITY",
    "STATE",
    "ENCOUNTERS",
    "PROCEDURES"
]

providers_clean = providers[provider_columns].copy()

providers_clean = providers_clean.rename(
    columns={
        "Id": "PROVIDER_ID",
        "ORGANIZATION": "ORGANIZATION_ID",
        "ENCOUNTERS": "RECORDED_ENCOUNTERS",
        "PROCEDURES": "RECORDED_PROCEDURES"
    }
)


# ==========================================================
# ORGANIZATIONS
# ==========================================================

print("Cleaning organizations...")

# Keep fields relevant to organizational analysis.
# Remove street address, phone, NPI and coordinates.

organization_columns = [
    "Id",
    "NAME",
    "CITY",
    "STATE",
    "REVENUE",
    "UTILIZATION"
]

organizations_clean = organizations[
    organization_columns
].copy()

organizations_clean = organizations_clean.rename(
    columns={
        "Id": "ORGANIZATION_ID",
        "NAME": "ORGANIZATION_NAME",
        "REVENUE": "RECORDED_REVENUE",
        "UTILIZATION": "RECORDED_UTILIZATION"
    }
)


# ==========================================================
# RELATIONSHIP VALIDATION
# ==========================================================

print("\nValidating relationships...")

# Load core processed tables for key validation

patients = pd.read_csv(
    PROCESSED_DIR / "patients_clean.csv"
)

encounters = pd.read_csv(
    PROCESSED_DIR / "encounters_clean.csv"
)

patient_ids = set(patients["PATIENT_ID"])
encounter_ids = set(encounters["ENCOUNTER_ID"])
provider_ids = set(providers_clean["PROVIDER_ID"])
organization_ids = set(
    organizations_clean["ORGANIZATION_ID"]
)


condition_patient_missing = (
    ~conditions_clean["PATIENT_ID"].isin(patient_ids)
).sum()

condition_encounter_missing = (
    ~conditions_clean["ENCOUNTER_ID"].isin(encounter_ids)
).sum()

procedure_patient_missing = (
    ~procedures_clean["PATIENT_ID"].isin(patient_ids)
).sum()

procedure_encounter_missing = (
    ~procedures_clean["ENCOUNTER_ID"].isin(encounter_ids)
).sum()

provider_org_missing = (
    ~providers_clean["ORGANIZATION_ID"].isin(
        organization_ids
    )
).sum()

encounter_provider_missing = (
    ~encounters["PROVIDER"].isin(provider_ids)
).sum()

encounter_org_missing = (
    ~encounters["ORGANIZATION"].isin(
        organization_ids
    )
).sum()


print(
    "Conditions with unmatched patient:",
    condition_patient_missing
)

print(
    "Conditions with unmatched encounter:",
    condition_encounter_missing
)

print(
    "Procedures with unmatched patient:",
    procedure_patient_missing
)

print(
    "Procedures with unmatched encounter:",
    procedure_encounter_missing
)

print(
    "Providers with unmatched organization:",
    provider_org_missing
)

print(
    "Encounters with unmatched provider:",
    encounter_provider_missing
)

print(
    "Encounters with unmatched organization:",
    encounter_org_missing
)


# ==========================================================
# BASIC DATA QUALITY CHECKS
# ==========================================================

print("\nData quality checks...")

print(
    "Duplicate condition rows:",
    conditions_clean.duplicated().sum()
)

print(
    "Duplicate procedure rows:",
    procedures_clean.duplicated().sum()
)

print(
    "Duplicate provider IDs:",
    providers_clean["PROVIDER_ID"].duplicated().sum()
)

print(
    "Duplicate organization IDs:",
    organizations_clean[
        "ORGANIZATION_ID"
    ].duplicated().sum()
)

print(
    "Negative procedure durations:",
    (
        procedures_clean["PROCEDURE_DURATION_MIN"] < 0
    ).sum()
)


# ==========================================================
# SAVE PROCESSED TABLES
# ==========================================================

print("\nSaving processed tables...")

conditions_clean.to_csv(
    PROCESSED_DIR / "conditions_clean.csv",
    index=False
)

procedures_clean.to_csv(
    PROCESSED_DIR / "procedures_clean.csv",
    index=False
)

providers_clean.to_csv(
    PROCESSED_DIR / "providers_clean.csv",
    index=False
)

organizations_clean.to_csv(
    PROCESSED_DIR / "organizations_clean.csv",
    index=False
)


print("\nSUCCESS")
print("=" * 60)

print(f"Conditions:    {len(conditions_clean):,}")
print(f"Procedures:    {len(procedures_clean):,}")
print(f"Providers:     {len(providers_clean):,}")
print(f"Organizations: {len(organizations_clean):,}")

print("\nProcessed related tables saved successfully.")