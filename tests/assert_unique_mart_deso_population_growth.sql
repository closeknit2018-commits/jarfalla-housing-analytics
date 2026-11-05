
-- Each DeSO area should have only one row
-- per year and geography version.

SELECT
    geography_version,
    region_code,
    reference_year,
    COUNT(*) AS duplicate_count
FROM {{ ref('mart_deso_population_growth') }}
GROUP BY
    geography_version,
    region_code,
    reference_year
HAVING COUNT(*) > 1
