
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

from config import RAW_DIR, TIMEOUT

BASE_URL = "https://statistikdatabasen.scb.se/api/v2/tables"

HISTORICAL_START_YEAR = 1968
HISTORICAL_END_YEAR = 2024
NEW_DATA_START_YEAR = 2025

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_scb_data(table_id: str, params: dict) -> dict:
    """Fetch JSON data from an SCB API table."""

    url = f"{BASE_URL}/{table_id}/data"

    logger.info("Requesting SCB table %s", table_id)

    response = requests.get(url, params=params, timeout=TIMEOUT)

    if not response.ok:
        print("SCB status code:", response.status_code)
        print("SCB error response:", response.text)

    response.raise_for_status()

    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise ValueError(
            f"SCB returned a response that is not valid JSON: {table_id}"
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError(
            f"Unexpected JSON structure for table {table_id}"
        )

    logger.info("Received a valid JSON response for %s", table_id)

    return payload


def save_raw_data(payload: dict, table_id: str) -> Path:
    """Save the original API response without transforming it."""

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    output_path = RAW_DIR / f"{table_id}_{timestamp}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2,
        )

    logger.info("Raw data saved to %s", output_path)

    return output_path


def extract_historical_population() -> Path:
    """Extract historical population data, 1968-2024."""

    params = {
        "lang": "sv",
        "valueCodes[ContentsCode]": "BE0101N1",
        "valueCodes[Region]": "0123",
        "valueCodes[Civilstand]": "OG,G,SK,ÄNKL",
        "valueCodes[Alder]": (
            "-4,5-9,10-14,15-19,20-24,25-29,"
            "30-34,35-39,40-44,45-49,50-54,55-59,"
            "60-64,65-69,70-74,75-79,80-84,85-89,"
            "90-94,95-99,100+,us"
        ),
        "valueCodes[Kon]": "1,2",
        "valueCodes[Tid]": ",".join(
            str(year) for year in range(
                HISTORICAL_START_YEAR,
                HISTORICAL_END_YEAR + 1,)
        ),
        "codelist[Region]": "vs_RegionKommun07",
        "codelist[Alder]": "agg_Ålder5år",
        "outputValues[Alder]": "aggregated",
    }

    payload = fetch_scb_data("TAB638", params)

    return save_raw_data(payload, "TAB638")


def get_available_year_end_periods(
    start_year: int = 2025,
) -> list[str]:
    """Find available December periods from SCB metadata."""

    url = (
        "https://statistikdatabasen.scb.se/api/v2/"
        "tables/TAB6471/metadata"
    )

    response = requests.get(
        url,
        params={"lang": "sv"},
        timeout=TIMEOUT,
    )

    if not response.ok:
        print("SCB status code:", response.status_code)
        print("SCB error response:", response.text)

    response.raise_for_status()

    metadata = response.json()
    dimensions = metadata["dimension"]
    time_codes = dimensions["Tid"]["category"]["index"]

    year_end_periods = [
        period
        for period in time_codes
        if (
            len(period) == 7
            and period[4:7] == "M12"
            and period[:4].isdigit()
            and int(period[:4]) >= start_year
        )
    ]

    year_end_periods = sorted(year_end_periods)

    if not year_end_periods:
        raise ValueError(
            f"No December periods found from {start_year} onward."
        )

    print("Available year-end periods:", year_end_periods)

    return year_end_periods


def extract_annual_population() -> Path:
    """Extract year-end population data from 2025 onward."""

    year_end_periods = get_available_year_end_periods(
        start_year=NEW_DATA_START_YEAR,
    )

    params = {
        "lang": "sv",
        "valueCodes[ContentsCode]": "000007SF",
        "valueCodes[Region]": "0123",
        "valueCodes[Alder]": "TotSA",
        "valueCodes[Kon]": "1,2",
        "valueCodes[Tid]": ",".join(year_end_periods),
    }

    payload = fetch_scb_data("TAB6471", params)

    return save_raw_data(payload, "TAB6471")


if __name__ == "__main__":
    historical_file = extract_historical_population()
    annual_file = extract_annual_population()
    print("\nExtraction completed.")
    print(f"Historical data: {historical_file}")
    print(f"Year_end population data: {annual_file}")
