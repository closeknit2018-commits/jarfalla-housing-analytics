--control sum of rows after loading
SELECT
	'Municipality' AS data_source,
	source_table_id,
	COUNT(*) AS row_count

FROM raw.scb_municipality_population
GROUP BY source_table_id

UNION ALL

SELECT
	'Deso' AS data_source,
	source_table_id,
	COUNT(*) AS row_count

FROM raw.scb_deso_population
GROUP BY source_table_id

ORDER BY data_source, source_table_id;


--control duplicate after loading scb_deso_population
SELECT
	source_table_id,
	region_code,
	reference_year,
	age_group_code,
	gender_code,
	COUNT(*) AS duplicate_count
FROM raw.scb_deso_population
GROUP BY
	source_table_id,
	region_code,
	reference_year,
	age_group_code,
	gender_code
HAVING COUNT(*) > 1;

--control duplicate after loading scb_municipality_population
SELECT
	source_table_id,
	region_code,
	reference_year,
	civil_status_code,
	age_group_code,
	gender_code,
	COUNT(*) AS duplicate_count
FROM raw.scb_municipality_population
GROUP BY
	source_table_id,
	region_code,
	reference_year,
	civil_status_code,
	age_group_code,
	gender_code
HAVING COUNT(*) > 1;


-- control null values scb_municipality_population
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE population IS NULL) AS null_population,
    COUNT(*) FILTER (WHERE region_code IS NULL) AS null_region,
    COUNT(*) FILTER (WHERE reference_year IS NULL) AS null_year,
    COUNT(*) FILTER (WHERE age_group_code IS NULL) AS null_age,
    COUNT(*) FILTER (WHERE gender_code IS NULL) AS null_gender
FROM raw.scb_municipality_population;

-- control null values scb_deso_population
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE population IS NULL) AS null_population,
    COUNT(*) FILTER (WHERE region_code IS NULL) AS null_region,
    COUNT(*) FILTER (WHERE reference_year IS NULL) AS null_year,
    COUNT(*) FILTER (WHERE age_group_code IS NULL) AS null_age,
    COUNT(*) FILTER (WHERE gender_code IS NULL) AS null_gender
FROM raw.scb_deso_population;
