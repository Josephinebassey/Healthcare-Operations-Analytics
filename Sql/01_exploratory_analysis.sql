
/*
============================================================
Healthcare Operations & Patient Outcomes Intelligence
Exploratory SQL Analysis
============================================================

Data Source:
Synthea synthetic healthcare data

Database:
HealthcareAnalytics

Purpose:
Explore patient demand, healthcare utilization, temporal
patterns, demographics, encounter duration, and healthcare
cost patterns.

Important:
This project uses synthetic healthcare data and does not
represent real patients or a real healthcare organization.
============================================================
*/

USE HealthcareAnalytics;
GO


/* =========================================================
   1. DATASET OVERVIEW
   ========================================================= */

-- Total number of patients
SELECT
    COUNT(*) AS Total_Patients
FROM dbo.patients;


-- Total number of encounters
SELECT
    COUNT(*) AS Total_Encounters
FROM dbo.encounters;


-- Unique patients represented in encounters
SELECT
    COUNT(DISTINCT PATIENT_ID) AS Unique_Patients_With_Encounters
FROM dbo.encounters;


-- Average encounters per patient
SELECT
    CAST(
        COUNT(*) * 1.0 /
        COUNT(DISTINCT PATIENT_ID)
        AS DECIMAL(10,2)
    ) AS Avg_Encounters_Per_Patient
FROM dbo.encounters;


/* =========================================================
   2. ENCOUNTER UTILIZATION
   ========================================================= */

-- Encounter volume by encounter class
SELECT
    ENCOUNTERCLASS,
    COUNT(*) AS Total_Encounters,
    CAST(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER ()
        AS DECIMAL(5,2)
    ) AS Percentage_Of_Encounters
FROM dbo.encounters
GROUP BY ENCOUNTERCLASS
ORDER BY Total_Encounters DESC;


/* =========================================================
   3. ENCOUNTER VOLUME BY YEAR
   ========================================================= */

SELECT
    ENCOUNTER_YEAR,
    COUNT(*) AS Total_Encounters
FROM dbo.encounters
GROUP BY ENCOUNTER_YEAR
ORDER BY ENCOUNTER_YEAR;


/* =========================================================
   4. RECENT ANNUAL ENCOUNTER VOLUME
   ========================================================= */

-- Restrict to 2017 onward for a more recent operational view.
-- Note: 2026 is a partial year in this dataset.

SELECT
    ENCOUNTER_YEAR,
    COUNT(*) AS Total_Encounters
FROM dbo.encounters
WHERE ENCOUNTER_YEAR >= 2017
GROUP BY ENCOUNTER_YEAR
ORDER BY ENCOUNTER_YEAR;


/* =========================================================
   5. ENCOUNTERS BY DAY OF WEEK
   ========================================================= */

SELECT
    DAY_OF_WEEK,
    COUNT(*) AS Total_Encounters
FROM dbo.encounters
GROUP BY DAY_OF_WEEK
ORDER BY Total_Encounters DESC;


/* =========================================================
   6. PATIENT DEMOGRAPHICS
   ========================================================= */

-- Gender distribution

SELECT
    GENDER,
    COUNT(*) AS Total_Patients
FROM dbo.patients
GROUP BY GENDER
ORDER BY Total_Patients DESC;


-- Race distribution

SELECT
    RACE,
    COUNT(*) AS Total_Patients
FROM dbo.patients
GROUP BY RACE
ORDER BY Total_Patients DESC;


-- Ethnicity distribution

SELECT
    ETHNICITY,
    COUNT(*) AS Total_Patients
FROM dbo.patients
GROUP BY ETHNICITY
ORDER BY Total_Patients DESC;


/* =========================================================
   7. AGE AT ENCOUNTER
   ========================================================= */

SELECT
    AGE_GROUP,
    COUNT(*) AS Total_Encounters
FROM dbo.patient_encounters
GROUP BY AGE_GROUP
ORDER BY
    CASE AGE_GROUP
        WHEN '0-17' THEN 1
        WHEN '18-29' THEN 2
        WHEN '30-44' THEN 3
        WHEN '45-59' THEN 4
        WHEN '60-74' THEN 5
        WHEN '75+' THEN 6
        ELSE 7
    END;


/* =========================================================
   8. ENCOUNTER DURATION BY CLASS
   ========================================================= */

SELECT
    ENCOUNTERCLASS,
    COUNT(*) AS Total_Encounters,

    CAST(
        AVG(ENCOUNTER_DURATION_MIN)
        AS DECIMAL(10,2)
    ) AS Avg_Duration_Minutes,

    CAST(
        MIN(ENCOUNTER_DURATION_MIN)
        AS DECIMAL(10,2)
    ) AS Min_Duration_Minutes,

    CAST(
        MAX(ENCOUNTER_DURATION_MIN)
        AS DECIMAL(10,2)
    ) AS Max_Duration_Minutes

FROM dbo.encounters
GROUP BY ENCOUNTERCLASS
ORDER BY Avg_Duration_Minutes DESC;


/* =========================================================
   9. ENCOUNTER COST ANALYSIS
   ========================================================= */

SELECT
    ENCOUNTERCLASS,

    COUNT(*) AS Total_Encounters,

    CAST(
        AVG(TOTAL_CLAIM_COST)
        AS DECIMAL(12,2)
    ) AS Avg_Claim_Cost,

    CAST(
        SUM(TOTAL_CLAIM_COST)
        AS DECIMAL(18,2)
    ) AS Total_Claim_Cost

FROM dbo.encounters
GROUP BY ENCOUNTERCLASS
ORDER BY Total_Claim_Cost DESC;


/* =========================================================
   10. PATIENT UTILIZATION
   ========================================================= */

-- Patients with the highest number of encounters

SELECT TOP 10
    PATIENT_ID,
    COUNT(*) AS Total_Encounters
FROM dbo.encounters
GROUP BY PATIENT_ID
ORDER BY Total_Encounters DESC;