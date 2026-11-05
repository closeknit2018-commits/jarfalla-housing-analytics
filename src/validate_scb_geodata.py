
import json
from collections import Counter

from config import RAW_DIR


def validate_regso_geodata() -> None:
    """Validate the downloaded SCB RegSO GeoJSON file."""

    file_path = RAW_DIR / "scb_regso_2025.geojson"

    print("Loading SCB RegSO geodata...")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    features = data.get("features", [])

    if not features:
        raise ValueError("No features found in the GeoJSON file.")

    print(f"Total features: {len(features)}")

    # Check whether RegSO codes are unique
    regso_codes = [
        feature.get("properties", {}).get("regsokod")
        for feature in features
    ]

    missing_codes = sum(code is None for code in regso_codes)
    duplicate_codes = {
        code: count
        for code, count in Counter(regso_codes).items()
        if code is not None and count > 1
    }

    print(f"Missing RegSO codes: {missing_codes}")
    print(f"Duplicate RegSO codes: {len(duplicate_codes)}")

    # Count features by municipality
    municipality_counts = Counter(
        feature.get("properties", {}).get("kommunkod")
        for feature in features
    )

    print("\nTop 10 municipalities by feature count:")

    for municipality_code, count in municipality_counts.most_common(10):
        print(f"Municipality {municipality_code}: {count} features")

    # Check geometry types
    geometry_counts = Counter(
        feature.get("geometry", {}).get("type")
        for feature in features
        if feature.get("geometry") is not None
    )

    print("\nGeometry types:")

    for geometry_type, count in geometry_counts.items():
        print(f"{geometry_type}: {count}")

    # Check required properties
    required_fields = [
        "regsokod",
        "regsonamn",
        "kommunkod",
        "version",
        "referensdatum",
    ]

    missing_fields = Counter()

    for feature in features:
        properties = feature.get("properties", {})

        for field in required_fields:
            if properties.get(field) in (None, ""):
                missing_fields[field] += 1

    print("\nMissing required values:")

    for field in required_fields:
        print(f"{field}: {missing_fields[field]}")

    print("\nGeodata validation completed.")


if __name__ == "__main__":
    validate_regso_geodata()
