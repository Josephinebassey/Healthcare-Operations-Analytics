
/*
============================================================
Healthcare Operations & Patient Outcomes Intelligence
Relational SQL Analysis

Data source: Synthea synthetic healthcare data
Database: HealthcareAnalytics

IMPORTANT:
This project uses synthetic healthcare records and does not
represent real patients, hospitals, providers, or financial
performance.
============================================================
*/

USE HealthcareAnalytics;
GO


/* =========================================================
1. MOST FREQUENT CONDITIONS
========================================================= */

SELECT TOP 15
    CONDITION_DESCRIPTION,
    COUNT(*) AS Condition_Records,
    COUNT(DISTINCT PATIENT_ID) AS Unique_Patients
FROM dbo.conditions
GROUP BY CONDITION_DESCRIPTION
ORDER BY Condition_Records DESC;


/* =========================================================
2. MOST FREQUENT PROCEDURES
========================================================= */

SELECT TOP 15
    PROCEDURE_DESCRIPTION,
    COUNT(*) AS Procedure_Count,
    COUNT(DISTINCT PATIENT_ID) AS Unique_Patients
FROM dbo.procedures
GROUP BY PROCEDURE_DESCRIPTION
ORDER BY Procedure_Count DESC;


/* =========================================================
3. PROCEDURE COST ANALYSIS
========================================================= */

SELECT TOP 15
    PROCEDURE_DESCRIPTION,
    COUNT(*) AS Procedure_Count,
    CAST(
        AVG(BASE_COST)
        AS DECIMAL(12,2)
    ) AS Avg_Base_Cost,
    CAST(
        SUM(BASE_COST)
        AS DECIMAL(18,2)
    ) AS Total_Base_Cost
FROM dbo.procedures
GROUP BY PROCEDURE_DESCRIPTION
HAVING COUNT(*) >= 10
ORDER BY Total_Base_Cost DESC;


/* =========================================================
4. ENCOUNTER CLASS + PROCEDURE UTILIZATION
========================================================= */

SELECT
    e.ENCOUNTERCLASS,
    COUNT(p.PROCEDURE_CODE) AS Procedure_Count,
    COUNT(DISTINCT e.ENCOUNTER_ID)
        AS Encounters_With_Procedures,
    COUNT(DISTINCT e.PATIENT_ID)
        AS Unique_Patients
FROM dbo.encounters e
INNER JOIN dbo.procedures p
    ON e.ENCOUNTER_ID = p.ENCOUNTER_ID
GROUP BY e.ENCOUNTERCLASS
ORDER BY Procedure_Count DESC;


/* =========================================================
5. PROCEDURE UTILIZATION BY AGE GROUP
========================================================= */

SELECT
    pe.AGE_GROUP,
    COUNT(p.PROCEDURE_CODE) AS Procedure_Count,
    COUNT(DISTINCT pe.PATIENT_ID)
        AS Unique_Patients
FROM dbo.patient_encounters pe
INNER JOIN dbo.procedures p
    ON pe.ENCOUNTER_ID = p.ENCOUNTER_ID
GROUP BY pe.AGE_GROUP
ORDER BY
    CASE pe.AGE_GROUP
        WHEN '0-17' THEN 1
        WHEN '18-29' THEN 2
        WHEN '30-44' THEN 3
        WHEN '45-59' THEN 4
        WHEN '60-74' THEN 5
        WHEN '75+' THEN 6
        ELSE 7
    END;


/* =========================================================
6. PROVIDER WORKLOAD

Calculated from encounter records rather than relying only
on the pre-recorded ENCOUNTERS field in providers.
========================================================= */

SELECT TOP 15
    p.PROVIDER_ID,
    p.SPECIALITY,
    p.CITY,
    COUNT(e.ENCOUNTER_ID)
        AS Calculated_Encounters,
    COUNT(DISTINCT e.PATIENT_ID)
        AS Unique_Patients
FROM dbo.providers p
INNER JOIN dbo.encounters e
    ON p.PROVIDER_ID = e.PROVIDER
GROUP BY
    p.PROVIDER_ID,
    p.SPECIALITY,
    p.CITY
ORDER BY Calculated_Encounters DESC;


/* =========================================================
7. ORGANIZATION UTILIZATION
========================================================= */

SELECT TOP 15
    o.ORGANIZATION_NAME,
    o.CITY,
    COUNT(e.ENCOUNTER_ID)
        AS Calculated_Encounters,
    COUNT(DISTINCT e.PATIENT_ID)
        AS Unique_Patients,
    CAST(
        SUM(e.TOTAL_CLAIM_COST)
        AS DECIMAL(18,2)
    ) AS Total_Claim_Cost
FROM dbo.organizations o
INNER JOIN dbo.encounters e
    ON o.ORGANIZATION_ID = e.ORGANIZATION
GROUP BY
    o.ORGANIZATION_ID,
    o.ORGANIZATION_NAME,
    o.CITY
ORDER BY Calculated_Encounters DESC;


/* =========================================================
8. CONDITION PATTERNS BY ENCOUNTER CLASS
========================================================= */

SELECT TOP 20
    e.ENCOUNTERCLASS,
    c.CONDITION_DESCRIPTION,
    COUNT(*) AS Condition_Records
FROM dbo.conditions c
INNER JOIN dbo.encounters e
    ON c.ENCOUNTER_ID = e.ENCOUNTER_ID
GROUP BY
    e.ENCOUNTERCLASS,
    c.CONDITION_DESCRIPTION
ORDER BY Condition_Records DESC;


/* =========================================================
9. PROCEDURE ACTIVITY OVER RECENT YEARS

2026 is a partial year and should not be compared directly
with completed calendar years.
========================================================= */

SELECT
    e.ENCOUNTER_YEAR,
    COUNT(p.PROCEDURE_CODE) AS Procedure_Count,
    COUNT(DISTINCT p.PATIENT_ID)
        AS Unique_Patients_With_Procedures
FROM dbo.procedures p
INNER JOIN dbo.encounters e
    ON p.ENCOUNTER_ID = e.ENCOUNTER_ID
WHERE e.ENCOUNTER_YEAR >= 2017
GROUP BY e.ENCOUNTER_YEAR
ORDER BY e.ENCOUNTER_YEAR;


/* =========================================================
10. MULTI-TABLE ANALYSIS:
AGE + ENCOUNTER CLASS + PROCEDURES
========================================================= */

SELECT
    pe.AGE_GROUP,
    pe.ENCOUNTERCLASS,
    COUNT(p.PROCEDURE_CODE) AS Procedure_Count
FROM dbo.patient_encounters pe
INNER JOIN dbo.procedures p
    ON pe.ENCOUNTER_ID = p.ENCOUNTER_ID
GROUP BY
    pe.AGE_GROUP,
    pe.ENCOUNTERCLASS
HAVING COUNT(p.PROCEDURE_CODE) >= 100
ORDER BY Procedure_Count DESC;