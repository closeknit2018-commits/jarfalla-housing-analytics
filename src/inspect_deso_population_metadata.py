
import json
import re
from pathlib import Path

import requests

TABLE_ID = "TAB6574"

URL = (
    "https://statistikdatabasen.scb.se/api/v2/"
    f"tables/{TABLE_ID}/metadata"
)

# Check OpenAPI Endpoint
urls = [
    "https://statistikdatabasen.scb.se/api/v2/swagger.json",
    "https://statistikdatabasen.scb.se/swagger/v1/swagger.json",
    "https://statistikdatabasen.scb.se/api/v2/openapi.json",
]

for url in urls:
    try:
        response = requests.get(url, timeout=30)

        print("\nURL:", url)
        print("STATUS:", response.status_code)
        print("CONTENT TYPE:", response.headers.get("Content-Type"))

        if response.status_code == 200:
            print(response.text[:3000])

    except requests.RequestException as error:
        print("ERROR:", error)

# Get data
response = requests.get(URL,params={"lang": "sv"},timeout=60,)
response.raise_for_status()

metadata = response.json()

print(f"\nTABLE: {metadata['label']}")
print(f"UPDATED: {metadata['updated']}")

dimensions = metadata["dimension"]

for dimension_id in metadata["id"]:

    dimension = dimensions[dimension_id]

    category = dimension["category"]
    indexes = category["index"]
    labels = category.get("label", {})

    print("\n" + "=" * 60)
    print(f"DIMENSION: {dimension_id}")
    print(f"LABEL: {dimension.get('label')}")
    print(f"NUMBER OF VALUES: {len(indexes)}")

    if dimension_id == "Region":

        print("\nJÄRFÄLLA REGIONS:")

        for code in indexes:
            if not code.startswith("0123"):
                continue

            label = labels.get(code, "No label")

            if code == "0123":
                region_type = "MUNICIPALITY"
            elif "_DeSO2025" in code:
                region_type = "DeSO 2025"
            elif "_RegSO2025" in code:
                region_type = "RegSO 2025"
            elif re.match(r"0123[A-Z]\d+", code):
                region_type = "LEGACY AREA"
            else:
                region_type = "OTHER"

            print(
                f"{code:30} | "
                f"{region_type:15} | {label}"
            )

    else:
        print("\nAVAILABLE VALUES:")

        for code in indexes:
            print(f"{code:20} | {labels.get(code, code)}")

# Save the metadata.
output_path = Path("data/raw/scb_tab6574_metadata.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as file:
    json.dump(metadata, file, ensure_ascii=False, indent=2)

print("\nMetadata inspection completed.")

# check old deso codes
region_index = metadata["dimension"]["Region"]["category"]["index"]
region_labels = metadata["dimension"]["Region"]["category"]["label"]

legacy_deso_codes = [
    code
    for code in region_index.keys()
    if code.startswith("0123")
    and "_DeSO2025" not in code
    and "_RegSO2025" not in code
]

print("Legacy Järfälla region codes:")

for code in legacy_deso_codes:
    print(code, "->", region_labels.get(code, code))

print("Total legacy codes:", len(legacy_deso_codes))

legacy_deso_codes = [
    code
    for code in region_index.keys()
    if code.startswith("0123C")
    and "_DeSO2025" not in code
]

print("Legacy DeSO codes:")

for code in legacy_deso_codes:
    print(code)

print("Total legacy DeSO codes:", len(legacy_deso_codes))

assert len(legacy_deso_codes) == 40
