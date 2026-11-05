
import requests

# Reuse the same API base URL as src/extract.py.
BASE_URL = "https://statistikdatabasen.scb.se/api/v2/tables"
TABLE_ID = "TAB638"
# "

url = f"{BASE_URL}/{TABLE_ID}/metadata"

response = requests.get(
    url,
    params={"lang": "sv"},
    timeout=30,
)
response.raise_for_status()

metadata = response.json()

# Print the main structure before inspecting details.
print("Top-level keys:")
print(list(metadata.keys()))

# Support the dimension key used by the metadata response.
dimensions = metadata.get(
    "dimension",
    metadata.get("dimensions", {}),
)

print("\nAvailable dimensions:")
for dimension_name in dimensions:
    print("-", dimension_name)

# Inspect the codes and labels for each dimension.
for dimension_name, details in dimensions.items():
    print(f"\n=== {dimension_name} ===")

    category = details.get("category", {})
    codes = category.get("index", {})
    labels = category.get("label", {})

    for code in codes:
        label = labels.get(code, "(no label)")
        print(f"{code} -> {label}")
