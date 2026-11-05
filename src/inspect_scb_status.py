
import json
from collections import Counter
from pathlib import Path

file_path = Path("data/raw/scb_deso_population_2025.json")

with file_path.open("r", encoding="utf-8") as file:
    data = json.load(file)

print("========== JSON-STAT2 INSPECTION ==========")

print("\n1. AVAILABLE FIELDS")
print(list(data.keys()))

# Check whether SCB provided observation status
status = data.get("status")

print("\n2. STATUS INFORMATION")
print(f"Status field exists: {status is not None}")

if status is not None:
    print(f"Status entries: {len(status)}")
    print(f"Status distribution: {Counter(status)}")
else:
    print("No status array provided.")

# Inspect value distribution by year
dimensions = data["dimension"]
ids = data["id"]
sizes = data["size"]
values = data["value"]

positions = {}

for dimension_id in ids:
    index = dimensions[dimension_id]["category"]["index"]

    positions[dimension_id] = {
        code: position
        for code, position in index.items()
    }

print("\n3. RAW OBSERVATIONS BY YEAR")

for year in ["2010", "2023", "2024", "2025"]:

    year_position = positions["Tid"][year]

    year_values = []

    # Iterate through all combinations except year
    from itertools import product

    other_dimensions = [
        dimension_id
        for dimension_id in ids
        if dimension_id != "Tid"
    ]

    categories = [
        list(positions[dimension_id].keys())
        for dimension_id in other_dimensions
    ]

    for combination in product(*categories):

        selected = dict(zip(other_dimensions, combination))
        selected["Tid"] = year

        flat_index = 0

        for dimension_id, size in zip(ids, sizes):
            position = positions[dimension_id][selected[dimension_id]]
            flat_index = flat_index * size + position

        year_values.append(values[flat_index])

    print(
        f"{year}: "
        f"count={len(year_values)}, "
        f"zeros={sum(v == 0 for v in year_values)}, "
        f"positive={sum(v > 0 for v in year_values)}"
    )

print("\n========== INSPECTION COMPLETED ==========")
