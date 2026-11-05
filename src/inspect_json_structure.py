
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

FILES = [
    "TAB638_20261026T133900Z.json",
    "TAB6471_20261026T133903Z.json",
    "scb_deso_population_2018.json",
    "scb_deso_population_2025.json",
]


def inspect_file(file_name):
    file_path = RAW_DIR / file_name

    print(f"\n{'=' * 70}")
    print(f"FILE: {file_name}")
    print("=" * 70)

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    print("Dataset ID:", data.get("id"))
    print("Dataset size:", data.get("size"))
    print("Number of observations:", len(data.get("value", [])))

    print("\nDimensions:")

    for dimension_id in data.get("id", []):
        dimension = data["dimension"][dimension_id]
        category = dimension["category"]

        index = category["index"]

        if isinstance(index, dict):
            codes = sorted(index, key=index.get)
        else:
            codes = index

        print(f"\nDimension: {dimension_id}")
        print("Number of categories:", len(codes))
        print("First 5 codes:", codes[:5])

    print("\nFirst 5 values:", data.get("value", [])[:5])


def main():
    for file_name in FILES:
        inspect_file(file_name)


if __name__ == "__main__":
    main()
