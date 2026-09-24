
import pandas as pd
from pathlib import Path

# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Healthcare Operations Analytics")
print("=" * 60)
print("Loading raw datasets...")


# ==========================================================
# LOAD DATA
# ==========================================================

patients = pd.read_csv(RAW_DIR / "patients.csv")
encounters = pd.read_csv(RAW_DIR / "encounters.csv")
conditions = pd.read_csv(RAW_DIR / "conditions.csv")
procedures = pd.read_csv(RAW_DIR / "procedures.csv")
providers = pd.read_csv(RAW_DIR / "providers.csv")
organizations = pd.read_csv(RAW_DIR / "organizations.csv")

print("\nRaw datasets loaded successfully.")

print(f"Patients:      {len(patients):,}")
print(f"Encounters:    {len(encounters):,}")
print(f"Conditions:    {len(conditions):,}")
print(f"Procedures:    {len(procedures):,}")
print(f"Providers:     {len(providers):,}")
print(f"Organizations: {len(organizations):,}")


# ==========================================================
# CLEAN PATIENT DATA
# ==========================================================

print("\nCleaning patient data...")

# Keep only analytically useful fields.
# Synthetic identifiers such as SSN/passport and personal names
# are deliberately excluded from the processed dataset.

patient_columns = [
    "Id",
    "BIRTHDATE",
    "DEATHDATE",
    "MARITAL",
    "RACE",
    "ETHNICITY",
    "GENDER",
    "CITY",
    "STATE",
    "COUNTY",
    "ZIP",
    "HEALTHCARE_EXPENSES",
    "HEALTHCARE_COVERAGE",
    "INCOME"
]

patients_clean = patients[patient_columns].copy()

patients_clean["BIRTHDATE"] = pd.to_datetime(
    patients_clean["BIRTHDATE"],
    errors="coerce"
)

patients_clean["DEATHDATE"] = pd.to_datetime(
    patients_clean["DEATHDATE"],
    errors="coerce"
)

# Rename patient key for clarity
patients_clean = patients_clean.rename(
    columns={"Id": "PATIENT_ID"}
)


# ==========================================================
# CLEAN ENCOUNTER DATA
# ==========================================================

print("Cleaning encounter data...")

encounters_clean = encounters.copy()

encounters_clean["START"] = pd.to_datetime(
    encounters_clean["START"],
    errors="coerce",
    utc=True
)

encounters_clean["STOP"] = pd.to_datetime(
    encounters_clean["STOP"],
    errors="coerce",
    utc=True
)

# Rename keys for clarity
encounters_clean = encounters_clean.rename(
    columns={
        "Id": "ENCOUNTER_ID",
        "PATIENT": "PATIENT_ID"
    }
)


# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

print("Creating analytical features...")

encounters_clean["ENCOUNTER_YEAR"] = (
    encounters_clean["START"].dt.year
)

encounters_clean["ENCOUNTER_MONTH"] = (
    encounters_clean["START"].dt.month
)

encounters_clean["ENCOUNTER_MONTH_NAME"] = (
    encounters_clean["START"].dt.month_name()
)

encounters_clean["DAY_OF_WEEK"] = (
    encounters_clean["START"].dt.day_name()
)

encounters_clean["ENCOUNTER_DURATION_MIN"] = (
    encounters_clean["STOP"] -
    encounters_clean["START"]
).dt.total_seconds() / 60


# ==========================================================
# JOIN PATIENT + ENCOUNTER DATA
# ==========================================================

print("Creating patient-encounter analytical table...")

patient_encounters = encounters_clean.merge(
    patients_clean,
    on="PATIENT_ID",
    how="left",
    validate="many_to_one"
)


# ==========================================================
# AGE AT ENCOUNTER
# ==========================================================

# Remove timezone information from encounter timestamp
# so it can be compared with BIRTHDATE.

encounter_date = patient_encounters["START"].dt.tz_localize(None)

age_in_years = (
    encounter_date - patient_encounters["BIRTHDATE"]
).dt.days / 365.25

patient_encounters["AGE_AT_ENCOUNTER"] = (
    age_in_years
    .apply(lambda x: int(x) if pd.notna(x) else pd.NA)
    .astype("Int64")
)

# ==========================================================
# AGE GROUP
# ==========================================================

def create_age_group(age):

    if pd.isna(age):
        return "Unknown"
    elif age < 18:
        return "0-17"
    elif age < 30:
        return "18-29"
    elif age < 45:
        return "30-44"
    elif age < 60:
        return "45-59"
    elif age < 75:
        return "60-74"
    else:
        return "75+"


patient_encounters["AGE_GROUP"] = (
    patient_encounters["AGE_AT_ENCOUNTER"]
    .apply(create_age_group)
)


# ==========================================================
# DATA VALIDATION
# ==========================================================

print("\nValidating processed data...")

print(
    "Duplicate patient IDs:",
    patients_clean["PATIENT_ID"].duplicated().sum()
)

print(
    "Duplicate encounter IDs:",
    encounters_clean["ENCOUNTER_ID"].duplicated().sum()
)

print(
    "Encounters without matching patient:",
    patient_encounters["BIRTHDATE"].isna().sum()
)

print(
    "Negative encounter durations:",
    (patient_encounters["ENCOUNTER_DURATION_MIN"] < 0).sum()
)

print(
    "Missing encounter start dates:",
    patient_encounters["START"].isna().sum()
)


# ==========================================================
# SAVE PROCESSED DATA
# ==========================================================

print("\nSaving processed datasets...")

patients_clean.to_csv(
    PROCESSED_DIR / "patients_clean.csv",
    index=False
)

encounters_clean.to_csv(
    PROCESSED_DIR / "encounters_clean.csv",
    index=False
)

patient_encounters.to_csv(
    PROCESSED_DIR / "patient_encounters.csv",
    index=False
)

print("\nSUCCESS")
print("=" * 60)

print(f"Clean patients: {len(patients_clean):,}")
print(f"Clean encounters: {len(encounters_clean):,}")
print(f"Patient-encounter records: {len(patient_encounters):,}")

print(
    f"Unique patients represented: "
    f"{patient_encounters['PATIENT_ID'].nunique():,}"
)

print("\nProcessed files saved to:")
print(PROCESSED_DIR)