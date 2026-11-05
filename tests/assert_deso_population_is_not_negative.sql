-- Population must never be negative.

SELECT
    region_code,
    geography_version,
    reference_year,
    population
FROM {{ ref('stg_scb__deso_population') }}
WHERE population < 0
