
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
IMAGE_DIR = PROJECT_ROOT / "images"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)

print("Healthcare Operations Analytics - Python EDA")
print("=" * 65)


# ==========================================================
# LOAD DATA
# ==========================================================

encounters = pd.read_csv(
    PROCESSED_DIR / "encounters_clean.csv"
)

patient_encounters = pd.read_csv(
    PROCESSED_DIR / "patient_encounters.csv"
)

procedures = pd.read_csv(
    PROCESSED_DIR / "procedures_clean.csv"
)

print(f"\nEncounters: {len(encounters):,}")
print(f"Patient-encounters: {len(patient_encounters):,}")
print(f"Procedures: {len(procedures):,}")


# ==========================================================
# 1. ENCOUNTER VOLUME BY CLASS
# ==========================================================

encounter_class = (
    encounters["ENCOUNTERCLASS"]
    .value_counts()
    .sort_values()
)

plt.figure(figsize=(10, 6))
encounter_class.plot(kind="barh")

plt.title("Encounter Volume by Class")
plt.xlabel("Number of Encounters")
plt.ylabel("Encounter Class")
plt.tight_layout()

plt.savefig(
    IMAGE_DIR / "encounter_volume_by_class.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ==========================================================
# 2. RECENT ENCOUNTER TREND
# ==========================================================

recent = encounters[
    encounters["ENCOUNTER_YEAR"].between(2017, 2025)
]

annual_encounters = (
    recent.groupby("ENCOUNTER_YEAR")
    .size()
)

plt.figure(figsize=(10, 6))

plt.plot(
    annual_encounters.index,
    annual_encounters.values,
    marker="o"
)

plt.title("Annual Encounter Volume, 2017-2025")
plt.xlabel("Year")
plt.ylabel("Number of Encounters")
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    IMAGE_DIR / "annual_encounter_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ==========================================================
# 3. ENCOUNTER DURATION DISTRIBUTION
# ==========================================================

duration_summary = (
    encounters.groupby("ENCOUNTERCLASS")
    ["ENCOUNTER_DURATION_MIN"]
    .agg(
        Encounter_Count="count",
        Mean_Duration="mean",
        Median_Duration="median",
        Min_Duration="min",
        Max_Duration="max"
    )
    .sort_values(
        "Median_Duration",
        ascending=False
    )
)

print("\nENCOUNTER DURATION SUMMARY")
print("-" * 65)
print(duration_summary.round(2).to_string())

# ==========================================================
# 4. MEAN VS MEDIAN DURATION
# ==========================================================

duration_plot = (
    duration_summary[
        ["Mean_Duration", "Median_Duration"]
    ]
    .sort_values("Median_Duration")
)

duration_plot.plot(
    kind="barh",
    figsize=(10, 7)
)

plt.title("Mean vs Median Encounter Duration")
plt.xlabel("Duration (Minutes)")
plt.ylabel("Encounter Class")
plt.tight_layout()

plt.savefig(
    IMAGE_DIR / "mean_vs_median_duration.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ==========================================================
# 5. PATIENT UTILIZATION DISTRIBUTION
# ==========================================================

patient_utilization = (
    encounters.groupby("PATIENT_ID")
    .size()
    .rename("Encounter_Count")
)

print("\nPATIENT UTILIZATION SUMMARY")
print("-" * 65)

print(
    patient_utilization.describe(
        percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    ).round(2)
)

plt.figure(figsize=(10, 6))

plt.hist(
    patient_utilization,
    bins=40
)

plt.title("Distribution of Encounters per Patient")
plt.xlabel("Number of Encounters")
plt.ylabel("Number of Patients")
plt.tight_layout()

plt.savefig(
    IMAGE_DIR / "patient_utilization_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ==========================================================
# 6. AGE GROUP PROCEDURE UTILIZATION
# ==========================================================

procedure_age = procedures.merge(
    patient_encounters[
        ["ENCOUNTER_ID", "AGE_GROUP"]
    ],
    on="ENCOUNTER_ID",
    how="left",
    validate="many_to_one"
)

age_order = [
    "0-17",
    "18-29",
    "30-44",
    "45-59",
    "60-74",
    "75+"
]

age_procedure_counts = (
    procedure_age["AGE_GROUP"]
    .value_counts()
    .reindex(age_order)
)

plt.figure(figsize=(10, 6))

age_procedure_counts.plot(
    kind="bar"
)

plt.title("Procedure Volume by Age Group")
plt.xlabel("Age Group at Encounter")
plt.ylabel("Number of Procedures")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    IMAGE_DIR / "procedure_volume_by_age.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ==========================================================
# FINISH
# ==========================================================

print("\nSUCCESS")
print("=" * 65)

print("Python EDA completed.")
print(f"Charts saved to: {IMAGE_DIR}")

print("\nGenerated charts:")
for chart in sorted(IMAGE_DIR.glob("*.png")):
    print(f"- {chart.name}")