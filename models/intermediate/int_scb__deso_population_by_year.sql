
-- Prepare total population by DeSO area and year.
-- Keep only observations representing all ages and genders.

SELECT
    population_id,
    geography_version,
    region_code,
    reference_year,
    population,
    source_table_id,
    source_file_name,
    extracted_at,
    loaded_at

FROM {{ ref('stg_scb__deso_population') }}

WHERE
    age_group_code = 'totalt'
    AND gender_code = '1+2'
    AND contents_code = '000007Y7'
