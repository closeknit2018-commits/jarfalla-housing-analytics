-- control total rows
SELECT COUNT(*) AS total_rows
FROM public.mart_deso_population_growth;

--control result table mart_deso_population_growth
SELECT *
FROM public.mart_deso_population_growth
ORDER BY
	geography_version,
	region_code,
	reference_year
LIMIT 20;

--control geography versions
SELECT
	geography_version,
	COUNT(*) AS total_rows,
	COUNT(population_change) AS rows_with_growth,
	MIN(reference_year) AS first_year,
	MAX(reference_year) AS last_year
FROM public.mart_deso_population_growth
GROUP BY geography_version
ORDER BY geography_version;
