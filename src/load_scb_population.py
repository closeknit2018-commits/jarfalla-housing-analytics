import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# --------------------------------------------------
# Configuration
# --------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
load_dotenv(PROJECT_DIR / ".env")

BATCH_SIZE = 1000

FILES = {
    "municipality": [
        "TAB638_20261026T133900Z.json",
        "TAB6471_20261026T133903Z.json",],
    "deso": [
        "scb_deso_population_2018.json",
        "scb_deso_population_2025.json",],
}

EXPECTED_COUNTS = {
    "TAB638": 10032,
    "TAB6471": 2,
    "DeSO2018": 30240,
    "DeSO2025": 4752,
}


# --------------------------------------------------
# Database connection
# --------------------------------------------------
def get_connection(target="local"):
    if target == "local":
        return psycopg.connect(
            host=os.getenv("DBT_HOST"),
            port=os.getenv("DBT_PORT"),
            user=os.getenv("DBT_USER"),
            password=os.getenv("DBT_ENV_SECRET_PASSWORD"),
            dbname=os.getenv("DBT_DATABASE"),
        )
    elif target == "neon":
        return psycopg.connect(
            host=os.getenv("NEON_DB_HOST"),
            port=os.getenv("NEON_DB_PORT"),
            user=os.getenv("NEON_DB_USER"),
            password=os.getenv("NEON_DB_PASSWORD"),
            dbname=os.getenv("NEON_DB_DATABASE"),
            sslmode="require",
        )
    else:
        raise ValueError("Invalid database target. Choose 'local' or 'neon'."
        )

# --------------------------------------------------
# JSON-stat2 helpers
# --------------------------------------------------

def get_dimension_codes(dimension):
    index = dimension["category"]["index"]

    if isinstance(index, dict):
        return sorted(index, key=index.get)

    return index


def get_observations(data):
    dimension_ids = data["id"]
    dimension_sizes = data["size"]
    values = data["value"]

    dimension_codes = {
        dimension_id: get_dimension_codes(
            data["dimension"][dimension_id]
        )
        for dimension_id in dimension_ids
    }

    observations = []

    for flat_index, population in enumerate(values):

        coordinates = []
        remaining = flat_index

        # Decode the flat JSON-stat2 array position.
        for position, dimension_size in enumerate(dimension_sizes):
            multiplier = 1

            for later_size in dimension_sizes[position + 1:]:
                multiplier *= later_size

            coordinate = remaining // multiplier
            remaining %= multiplier

            coordinates.append(coordinate)

        observation = {}

        for position, dimension_id in enumerate(dimension_ids):
            coordinate = coordinates[position]

            observation[dimension_id] = (
                dimension_codes[dimension_id][coordinate]
            )

        observation["population"] = population

        observations.append(observation)

    return observations


def read_json(file_name):
    file_path = RAW_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"JSON file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# Municipality transformation
# --------------------------------------------------

def prepare_municipality_rows(file_name):
    data = read_json(file_name)
    observations = get_observations(data)

    source_table_id = (
        "TAB638" if file_name.startswith("TAB638")
        else "TAB6471"
    )

    extracted_at = datetime.now(timezone.utc)

    rows = []

    for item in observations:
        # TAB6471 uses YYYYMM format, e.g. 2025M12.
        reference_year = int(item["Tid"][:4])

        rows.append((
            source_table_id,
            file_name,
            item["Region"],
            reference_year,
            item.get("Civilstand"),
            item["Alder"],
            item["Kon"],
            item["ContentsCode"],
            item["population"],
            extracted_at,
        ))

    return rows


# --------------------------------------------------
# DeSO transformation
# --------------------------------------------------

def prepare_deso_rows(file_name):
    data = read_json(file_name)
    observations = get_observations(data)

    if "2018" in file_name:
        geography_version = "DeSO2018"
    else:
        geography_version = "DeSO2025"

    source_file_name = (
        "Folkmängden per region efter ålder och kön. "
        "År 2010-2025 (TAB6574)"
    )

    extracted_at = datetime.now(timezone.utc)

    rows = []

    for item in observations:
        rows.append((
            "TAB6574",
            source_file_name,
            geography_version,
            item["Region"],
            int(item["Tid"]),
            item["Alder"],
            item["Kon"],
            item["ContentsCode"],
            item["population"],
            extracted_at,
        ))

    return rows


# --------------------------------------------------
# Batch loading
# --------------------------------------------------

def load_batches(cursor, sql, rows):
    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start:start + BATCH_SIZE]
        cursor.executemany(sql, batch)


def load_municipality(cursor, file_name):
    rows = prepare_municipality_rows(file_name)

    sql = """
        INSERT INTO raw.scb_municipality_population (
            source_table_id,
            source_file_name,
            region_code,
            reference_year,
            civil_status_code,
            age_group_code,
            gender_code,
            contents_code,
            population,
            extracted_at
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON CONFLICT ON CONSTRAINT unique_municipality_population
        DO UPDATE SET
            population = EXCLUDED.population,
            source_file_name = EXCLUDED.source_file_name,
            loaded_at = CURRENT_TIMESTAMP;
    """

    load_batches(cursor, sql, rows)

    print(
        f"Municipality: processed {len(rows)} rows "
        f"from {file_name}"
    )


def load_deso(cursor, file_name):
    rows = prepare_deso_rows(file_name)

    sql = """
        INSERT INTO raw.scb_deso_population (
            source_table_id,
            source_file_name,
            geography_version,
            region_code,
            reference_year,
            age_group_code,
            gender_code,
            contents_code,
            population,
            extracted_at
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON CONFLICT ON CONSTRAINT unique_deso_population
        DO UPDATE SET
            population = EXCLUDED.population,
            source_file_name = EXCLUDED.source_file_name,
            loaded_at = CURRENT_TIMESTAMP;
    """

    load_batches(cursor, sql, rows)

    print(
        f"DeSO: processed {len(rows)} rows "
        f"from {file_name}"
    )


# --------------------------------------------------
# Validation
# --------------------------------------------------

def validate_database(cursor):
    checks = [
        (
            "TAB638",
            """
            SELECT COUNT(*)
            FROM raw.scb_municipality_population
            WHERE source_table_id = 'TAB638'
            """,
        ),
        (
            "TAB6471",
            """
            SELECT COUNT(*)
            FROM raw.scb_municipality_population
            WHERE source_table_id = 'TAB6471'
            """,
        ),
        (
            "DeSO2018",
            """
            SELECT COUNT(*)
            FROM raw.scb_deso_population
            WHERE geography_version = 'DeSO2018'
            """,
        ),
        (
            "DeSO2025",
            """
            SELECT COUNT(*)
            FROM raw.scb_deso_population
            WHERE geography_version = 'DeSO2025'
            """,
        ),
    ]

    print("\nDATABASE VALIDATION")
    print("=" * 50)

    for name, sql in checks:
        cursor.execute(sql)
        actual_count = cursor.fetchone()[0]
        expected_count = EXPECTED_COUNTS[name]

        status = "PASS" if actual_count == expected_count else "FAIL"

        print(
            f"{name}: {actual_count} / "
            f"{expected_count} rows - {status}"
        )

        if actual_count != expected_count:
            raise ValueError(
                f"Unexpected row count for {name}"
            )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main(target="local"):
    print(f"Starting SCB population data loading to {target}...")

    with get_connection(target) as connection:
        with connection.cursor() as cursor:

            for file_name in FILES["municipality"]:
                load_municipality(cursor, file_name)

            for file_name in FILES["deso"]:
                load_deso(cursor, file_name)

            validate_database(cursor)

    print("\nSCB population data loading completed successfully.")


def test_neon_connection():
    print("Testing Neon connection...")

    with get_connection("neon") as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user;")
            result = cursor.fetchone()

            print(f"Database: {result[0]}")
            print(f"User: {result[1]}")

    print("Neon connection successful!")


if __name__ == "__main__":
   main("neon")
