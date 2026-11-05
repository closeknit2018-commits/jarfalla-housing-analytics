
-- Standardize SCB RegSO geographic data.
-- Keep only the RegSO areas belonging to Järfälla municipality.

select
    objectid,
    objektidentitet as object_identity,
    regsokod as regso_code,
    regsonamn as regso_name,
    lanskod as county_code,
    kommunkod as municipality_code,
    version as data_version,
    referensdatum as reference_date,
    geometry

from {{ source('scb_raw', 'regso_areas') }}

where kommunkod = '0123'
