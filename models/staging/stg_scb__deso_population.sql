-- Standardize population observations
-- from SCB DeSO population data.

SELECT
    population_id,
    source_table_id,
    source_file_name,
    geography_version,
    region_code,
    reference_year,
    age_group_code,
    gender_code,
    contents_code,
    population,
    extracted_at,
    loaded_at

FROM {{ source('scb_raw', 'scb_deso_population') }}
