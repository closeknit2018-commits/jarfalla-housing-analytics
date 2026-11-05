import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

from config import RAW_DIR, TIMEOUT

WFS_URL = ("https://geodata.scb.se/geoserver/stat/wfs")


def get_latest_regso_layer() -> tuple[str, int]:
    """Find the newest available RegSO layer from SCB."""

    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetCapabilities",
    }

    response = requests.get(
        WFS_URL,
        params=params,
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    layers = []

    for element in root.iter():
        if element.tag.endswith("Name") and element.text:
            layer_name = element.text.strip()

            match = re.search(
                r"(?:^|:)RegSO_(\d{4})$",
                layer_name,
                re.IGNORECASE,
            )

            if match:
                year = int(match.group(1))
                layers.append((layer_name, year))

    if not layers:
        raise ValueError(
            "Could not find a RegSO layer in WFS capabilities."
        )

    # Select the latest available year.
    layer_name, year = max(
        layers,
        key=lambda item: item[1],
    )

    print(f"Selected SCB layer: {layer_name}")
    print(f"Data year: {year}")

    return layer_name, year


def extract_regso_geodata() -> Path:
    """Download RegSO boundaries from SCB as GeoJSON."""

    layer_name, year = get_latest_regso_layer()

    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typeName": layer_name,
        "outputFormat": "json",
    }

    print("Downloading RegSO geodata from SCB...")

    response = requests.get(
        WFS_URL,
        params=params,
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("type") != "FeatureCollection":
        raise ValueError(
            "SCB response is not a GeoJSON FeatureCollection. "
            f"Response keys: {list(payload.keys())}"
        )

    features = payload.get("features", [])

    if not features:
        raise ValueError(
            "The SCB response contains no geographic features."
        )

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    output_path = (
        RAW_DIR / f"scb_regso_{year}.geojson"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file, indent=2,
            ensure_ascii=False,
        )

    print(f"Downloaded features: {len(features)}")
    print(f"Saved raw data to: {output_path}")

    return output_path


if __name__ == "__main__":
    extract_regso_geodata()
