
-- Standardize annual population observations
-- from SCB municipality data.

select
    population_id,

    source_table_id,
    source_file_name,

    region_code,
    reference_year,

    civil_status_code,
    age_group_code,
    gender_code,

    contents_code,
    population,

    extracted_at,
    loaded_at

from {{ source('scb_raw', 'scb_municipality_population') }}
