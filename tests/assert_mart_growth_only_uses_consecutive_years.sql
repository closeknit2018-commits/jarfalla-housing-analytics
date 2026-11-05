
-- Population growth must only use the previous calendar year.
-- Growth values must be NULL when the previous year is missing.

SELECT
    geography_version,
    region_code,
    reference_year,
    previous_reference_year,
    previous_population,
    population_change,
    population_growth_percent

FROM {{ ref('mart_deso_population_growth') }}
WHERE
    (previous_population IS NOT NULL
    AND previous_reference_year IS DISTINCT FROM reference_year - 1)

    OR
    (previous_population IS NULL
    AND previous_reference_year = reference_year - 1)

    OR
    (previous_population IS NULL
    AND(population_change IS NOT NULL OR population_growth_percent IS NOT NULL))
