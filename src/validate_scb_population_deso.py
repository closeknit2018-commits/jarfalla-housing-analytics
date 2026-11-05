
import json
from pathlib import Path

# Define the input file
file_path = Path("data/raw/scb_deso_population_2025.json")

# Load JSON-stat2 data
with file_path.open("r", encoding="utf-8") as file:
    data = json.load(file)

print("========== DATASET VALIDATION ==========")

# 1. Check dimensions
dimension_ids = data["id"]
dimension_sizes = data["size"]

print("\n1. DIMENSIONS")

for dimension, size in zip(dimension_ids, dimension_sizes):
    print(f"{dimension}: {size}")

# 2. Calculate expected cells
expected_cells = 1

for size in dimension_sizes:
    expected_cells *= size

print(f"\nExpected cells: {expected_cells}")

# 3. Check actual observations
values = data.get("value", [])

print(f"Actual observations: {len(values)}")

# 4. Check missing values
missing_values = sum(value is None for value in values)

print(f"Missing values: {missing_values}")

# 5. Check observation completeness
if len(values) == expected_cells:
    print("Observation count: PASS")
else:
    print("Observation count: CHECK")

# 6. Check metadata
print("\n6. METADATA")

print(f"Dataset: {data.get('label')}")
print(f"Source: {data.get('source')}")
print(f"Last updated: {data.get('updated')}")

print("\n========== VALIDATION 1 COMPLETED ==========")



import json
from pathlib import Path

file_path = Path("data/raw/scb_deso_population_2025.json")

with file_path.open("r", encoding="utf-8") as file:
    data = json.load(file)

dimensions = data["dimension"]
values = data["value"]

# Extract category codes and labels
def get_categories(dimension_name):
    category = dimensions[dimension_name]["category"]

    codes = sorted(
        category["index"].items(),
        key=lambda item: item[1]
    )

    labels = category.get("label", {})

    return [
        {
            "code": code,
            "label": labels.get(code, code)
        }
        for code, position in codes
    ]


regions = get_categories("Region")
ages = get_categories("Alder")
genders = get_categories("Kon")
years = get_categories("Tid")

print("========== DATA QUALITY CHECK ==========")

# 1. Check region codes
print("\n1. REGION CHECK")

invalid_regions = [
    region["code"]
    for region in regions
    if not region["code"].startswith("0123")
    or not region["code"].endswith("_DeSO2025")
]

print(f"Total regions: {len(regions)}")
print(f"Invalid regions: {len(invalid_regions)}")

if invalid_regions:
    print(invalid_regions)

# 2. Check years
print("\n2. YEAR CHECK")

year_codes = [year["code"] for year in years]

print(f"Years: {year_codes}")
print(f"Year count: {len(year_codes)}")

# 3. Check observation values
print("\n3. VALUE CHECK")

numeric_values = [
    value for value in values
    if isinstance(value, (int, float))
    and not isinstance(value, bool)
]

negative_values = [
    value for value in numeric_values
    if value < 0
]

print(f"Numeric values: {len(numeric_values)}")
print(f"Negative values: {len(negative_values)}")

# 4. Check category counts
print("\n4. CATEGORY CHECK")

print(f"Regions: {len(regions)}")
print(f"Age groups: {len(ages)}")
print(f"Genders: {len(genders)}")
print(f"Years: {len(years)}")

print("\n========== CHECK COMPLETED ==========")
