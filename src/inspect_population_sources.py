
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"

FILES = {
    "TAB638": RAW_DIR / "TAB638_20261026T133900Z.json",
    "TAB6471": RAW_DIR / "TAB6471_20261026T133903Z.json",
    "DeSO 2018": RAW_DIR / "scb_deso_population_2018.json",
    "DeSO 2025": RAW_DIR / "scb_deso_population_2025.json",
}


def inspect_file(name, file_path):

    print("\n" + "=" * 65)
    print(f"SOURCE: {name}")
    print("=" * 65)

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    print("Label:", data.get("label"))
    print("Source:", data.get("source"))
    print("Updated:", data.get("updated"))

    print("\nDIMENSIONS")

    for dimension_id in data.get("id", []):

        dimension = data["dimension"][dimension_id]

        category = dimension.get("category", {})
        index = category.get("index", {})
        labels = category.get("label", {})

        codes = list(index.keys())

        print(f"\nDimension: {dimension_id}")
        print("Number of categories:", len(codes))
        print("First 10 codes:")

        for code in codes[:10]:
            print(f"  {code}: {labels.get(code, '')}")

    if name == "TAB638":

        print("\nALL AGE CATEGORIES IN TAB638")

        age_dimension = data["dimension"]["Alder"]

        age_index = age_dimension["category"]["index"]
        age_labels = age_dimension["category"].get("label", {})

        for code in age_index.keys():
            print(f"{code}: {age_labels.get(code, '')}")

        print("\nALL YEARS IN TAB638")

        year_index = data["dimension"]["Tid"]["category"]["index"]

        print(list(year_index.keys()))

    print("\nDATA")

    print("Dimension order:", data.get("id"))
    print("Dimension sizes:", data.get("size"))
    print("Number of observations:", len(data.get("value", [])))

    print("First 10 values:", data.get("value", [])[:10])

    print("\nNOTES:", data.get("note"))


def main():

    for name, file_path in FILES.items():

        if not file_path.exists():
            print(f"\nFILE NOT FOUND: {file_path}")
            continue

        inspect_file(name, file_path)


if __name__ == "__main__":
    main()
