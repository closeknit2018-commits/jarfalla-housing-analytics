DROP TABLE IF EXISTS raw.scb_municipality_population;
CREATE TABLE raw.scb_municipality_population(
	population_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

	--source info
	source_table_id VARCHAR(50) NOT NULL,
	source_file_name TEXT NOT NULL,

	--geographic info
	region_code VARCHAR(4) NOT NULL,

	--annual time info
	reference_year SMALLINT NOT NULL,

	--population dimensions
	civil_status_code VARCHAR(10),
	age_group_code VARCHAR (10) NOT NULL,
	gender_code VARCHAR(10) NOT NULL,
	contents_code VARCHAR(20) NOT NULL,

	--population measure
	population INT,

	--ETL metadata
	extracted_At TIMESTAMPTZ NOT NULL,
	loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

	--validation constraints
	CONSTRAINT check_municipality_source
		CHECK(source_table_id IN ('TAB638', 'TAB6471')),

	CONSTRAINT check_municipality_region
		CHECK(region_code = '0123'),

	CONSTRAINT check_municipality_population
		CHECK(population IS NULL OR population >= 0),

	--prevent duplicate source observations
	CONSTRAINT unique_municipality_population
		UNIQUE NULLS NOT DISTINCT(
			source_table_id,
			region_code,
			reference_year,
			civil_status_code,
			age_group_code,
			gender_code,
			contents_code)
);


DROP TABLE IF EXISTS raw.scb_deso_population;
CREATE TABLE raw.scb_deso_population(
	population_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

	--source info
	source_table_id VARCHAR(50) NOT NULL,
	source_file_name TEXT NOT NULL,

	--geographic info
	geography_version VARCHAR(10) NOT NULL,
	region_code VARCHAR(20) NOT NULL,

	--time info
	reference_year SMALLINT NOT NULL,

	--population dimensions
	age_group_code VARCHAR(10) NOT NULL,
	gender_code VARCHAR(10) NOT NULL,
	contents_code VARCHAR (20) NOT NULL,

	--population measure
	population INT,

	--ETL metadata
	extracted_at TIMESTAMPTZ NOT NULL,
	loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

	--data validation
	CONSTRAINT check_deso_geography_version
		CHECK(geography_version IN ('DeSO2018', 'DeSO2025')),

	CONSTRAINT check_deso_population
		CHECK(population IS NULL OR population >=0),

	CONSTRAINT check_deso_source
		CHECK(source_table_id = 'TAB6574'),

	--business key: prevent duplicate observations
	CONSTRAINT unique_deso_population
		UNIQUE(
			source_table_id,
			geography_version,
			region_code,
			reference_year,
			age_group_code,
			gender_code,
			contents_code)
);

--we shall need filter region and year that why needs to create these index
CREATE INDEX IF NOT EXISTS idex_municipality_year
	ON raw.scb_municipality_population(reference_year);

CREATE INDEX IF NOT EXISTS idex_deso_region_year
	ON raw.scb_deso_population(
		geography_version,
		region_code,
		reference_year);
