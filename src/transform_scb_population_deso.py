
import csv
import json
from itertools import product
from pathlib import Path

# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

input_file = Path("data/raw/scb_deso_population_2025.json")
output_file = Path("data/bronze/scb_deso_population_long.csv")

output_file.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load JSON-stat2
# --------------------------------------------------

with input_file.open("r", encoding="utf-8") as file:
    data = json.load(file)

dimension_ids = data["id"]
dimension_sizes = data["size"]
observations = data["value"]


# --------------------------------------------------
# 3. Extract category codes and labels
# --------------------------------------------------

dimension_categories = {}
dimension_positions = {}

for dimension_id in dimension_ids:

    category = data["dimension"][dimension_id]["category"]

    # Sort codes according to their positions
    sorted_categories = sorted(
        category["index"].items(),
        key=lambda item: item[1]
    )

    codes = [code for code, position in sorted_categories]

    dimension_categories[dimension_id] = codes

    dimension_positions[dimension_id] = {
        code: position
        for code, position in sorted_categories
    }


# --------------------------------------------------
# 4. Validate dimension sizes
# --------------------------------------------------

for dimension_id, expected_size in zip(
    dimension_ids,
    dimension_sizes
):
    actual_size = len(dimension_categories[dimension_id])

    assert actual_size == expected_size, (
        f"{dimension_id}: expected {expected_size}, "
        f"got {actual_size}"
    )


# --------------------------------------------------
# 5. Create category combinations
# --------------------------------------------------

category_lists = [
    dimension_categories[dimension_id]
    for dimension_id in dimension_ids
]

records = []

for combination in product(*category_lists):

    # Calculate flattened observation index.
    # The last dimension changes fastest in JSON-stat2.
    flat_index = 0

    for dimension_id, code, size in zip(
        dimension_ids,
        combination,
        dimension_sizes
    ):
        position = dimension_positions[dimension_id][code]

        flat_index = flat_index * size + position

    population = observations[flat_index]

    region_code, age_code, gender_code, contents_code, year = (
        combination
    )

    records.append({
        "region_code": region_code,
        "age_group_code": age_code,
        "gender_code": gender_code,
        "contents_code": contents_code,
        "year": int(year),
        "population": population
    })


# --------------------------------------------------
# 6. Validate transformed records
# --------------------------------------------------

expected_rows = 38016

assert len(records) == expected_rows

assert all(
    record["population"] is not None
    for record in records
)

# Check unique business key
keys = [
    (
        record["region_code"],
        record["age_group_code"],
        record["gender_code"],
        record["contents_code"],
        record["year"]
    )
    for record in records
]

assert len(keys) == len(set(keys)), "Duplicate records found"


# --------------------------------------------------
# 7. Export CSV
# --------------------------------------------------

fieldnames = [
    "region_code",
    "age_group_code",
    "gender_code",
    "contents_code",
    "year",
    "population"
]

with output_file.open("w", encoding="utf-8", newline="") as file:

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(records)


# --------------------------------------------------
# 8. Print summary
# --------------------------------------------------

print("========== TRANSFORMATION SUMMARY ==========")

print(f"Input file: {input_file}")
print(f"Output file: {output_file}")
print(f"Total records: {len(records)}")
print(f"Unique keys: {len(set(keys))}")
print(f"Missing populations: {sum(r['population'] is None for r in records)}")

print("\nSample records:")

for record in records[:5]:
    print(record)

print("\nTransformation completed successfully!")
