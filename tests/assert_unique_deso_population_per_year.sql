-- Each DeSO area should have only one
-- total population observation per year and geography version.

SELECT
    COUNT(*) AS duplicate_count,
    geography_version,
    SUM(population) AS total_population,
    reference_year,
    region_code
FROM {{ ref('int_scb__deso_population_by_year') }}
GROUP BY
    geography_version,
    reference_year,
    region_code
HAVING COUNT(*) > 1
