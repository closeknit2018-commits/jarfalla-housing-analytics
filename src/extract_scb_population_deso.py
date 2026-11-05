
import json
from pathlib import Path

import requests

from inspect_deso_population_metadata import legacy_deso_codes

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

TABLE_ID = "TAB6574"

BASE_URL = "https://statistikdatabasen.scb.se/api/v2"

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_DIR / "data" / "raw"

METADATA_PATH = RAW_DIR / "scb_tab6574_metadata.json"

OUTPUT_2018 = RAW_DIR / "scb_deso_population_2018.json"
OUTPUT_2025 = RAW_DIR / "scb_deso_population_2025.json"

MUNICIPALITY_CODE = "0123"

CONTENTS_CODE = "000007Y7"

GENDER_CODES = ["1", "2", "1+2"]


# --------------------------------------------------
# LOAD METADATA
# --------------------------------------------------

def load_metadata():
    with METADATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# GET DIMENSION CODES
# --------------------------------------------------

def get_dimension_codes(metadata, dimension_name):
    return list(
        metadata["dimension"][dimension_name]
        ["category"]["index"].keys()
    )


# --------------------------------------------------
# GET DESO 2025 CODES
# --------------------------------------------------

def get_deso_2025_codes(metadata):
    region_index = get_dimension_codes(metadata, "Region")

    deso_codes = [
        code
        for code in region_index
        if code.startswith(MUNICIPALITY_CODE + "C")
        and code.endswith("_DeSO2025")
    ]

    if len(deso_codes) != 44:
        raise ValueError(
            f"Expected 44 DeSO 2025 areas, found {len(deso_codes)}"
        )

    return deso_codes


# --------------------------------------------------
# EXTRACT DATA FROM SCB
# --------------------------------------------------

def extract_population(
    session,
    metadata,
    region_codes,
    year_codes,
    output_path,
    geography_version
):
    age_codes = get_dimension_codes(metadata, "Alder")

    expected_regions = 40 if geography_version == "2018" else 44

    if len(region_codes) != expected_regions:
        raise ValueError(
            f"Expected {expected_regions} regions for DeSO {geography_version}"
        )

    if len(age_codes) != 18:
        raise ValueError(
            f"Expected 18 age groups, found {len(age_codes)}"
        )

    if not year_codes:
        raise ValueError("Year selection cannot be empty.")

    payload = {
        "selection": [
            {
                "variableCode": "Region",
                "valueCodes": region_codes
            },
            {
                "variableCode": "Alder",
                "valueCodes": age_codes
            },
            {
                "variableCode": "Kon",
                "valueCodes": GENDER_CODES
            },
            {
                "variableCode": "ContentsCode",
                "valueCodes": [CONTENTS_CODE]
            },
            {
                "variableCode": "Tid",
                "valueCodes": year_codes
            }
        ]
    }

    expected_cells = (
        len(region_codes)
        * len(age_codes)
        * len(GENDER_CODES)
        * len(year_codes)
    )

    print(f"\nExtracting DeSO {geography_version}")
    print("----------------------------------")
    print("Regions:", len(region_codes))
    print("Age groups:", len(age_codes))
    print("Years:", len(year_codes))
    print("Gender categories:", len(GENDER_CODES))
    print("Expected cells:", expected_cells)

    url = f"{BASE_URL}/tables/{TABLE_ID}/data"

    params = {
        "lang": "sv",
        "outputFormat": "json-stat2"
    }

    response = session.post(
        url,
        params=params,
        json=payload,
        timeout=120
    )

    print("HTTP Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    actual_cells = len(data.get("value", []))

    if actual_cells != expected_cells:
        raise ValueError(
            f"Cell count mismatch! Expected {expected_cells}, "
            f"received {actual_cells}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("Extraction completed.")
    print("Output:", output_path)
    print("Actual cells:", actual_cells)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    metadata = load_metadata()

    age_codes = get_dimension_codes(metadata, "Alder")
    available_years = get_dimension_codes(metadata, "Tid")

    # DeSO 2018: historical geography
    legacy_regions = legacy_deso_codes

    if len(legacy_regions) != 40:
        raise ValueError(
            f"Expected 40 legacy DeSO areas, found {len(legacy_regions)}"
        )

    years_2018 = [
        year for year in available_years
        if "2010" <= year <= "2023"
    ]

    # DeSO 2025: new geography
    regions_2025 = get_deso_2025_codes(metadata)

    years_2025 = [
    year for year in available_years
    if year in ["2024", "2025"]
    ]

    # Validate selections
    assert len(years_2018) == 14
    assert len(years_2025) == 2
    assert len(age_codes) == 18

    with requests.Session() as session:

        extract_population(
            session=session,
            metadata=metadata,
            region_codes=legacy_regions,
            year_codes=years_2018,
            output_path=OUTPUT_2018,
            geography_version="2018"
        )

        extract_population(
            session=session,
            metadata=metadata,
            region_codes=regions_2025,
            year_codes=years_2025,
            output_path=OUTPUT_2025,
            geography_version="2025"
        )


if __name__ == "__main__":
    main()
