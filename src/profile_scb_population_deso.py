
import json
from math import prod
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"


FILES = {
    "DeSO 2018": RAW_DIR / "scb_deso_population_2018.json",
    "DeSO 2025": RAW_DIR / "scb_deso_population_2025.json",
}


def profile_file(name, file_path):

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    dimensions = data["dimension"]
    dimension_ids = data["id"]
    sizes = data["size"]
    values = data["value"]

    # Build dimension lookup
    indexes = {
        dimension_id: dimensions[dimension_id]["category"]["index"]
        for dimension_id in dimension_ids
    }

    years = list(indexes["Tid"].keys())

    # Calculate flat-array strides
    strides = []

    for i in range(len(sizes)):
        strides.append(prod(sizes[i + 1:]))

    def get_position(region, age, gender, year):

        selected = {
            "Region": region,
            "Alder": age,
            "Kon": gender,
            "ContentsCode": "000007Y7",
            "Tid": year,
        }

        position = 0

        for i, dimension_id in enumerate(dimension_ids):
            category_code = selected[dimension_id]
            category_position = indexes[dimension_id][category_code]

            position += category_position * strides[i]

        return position

    regions = list(indexes["Region"].keys())
    ages = list(indexes["Alder"].keys())
    genders = list(indexes["Kon"].keys())

    print(f"\n{'=' * 55}")
    print(f"PROFILE: {name}")
    print(f"{'=' * 55}")

    print("Regions:", len(regions))
    print("Age groups:", len(ages))
    print("Years:", len(years))
    print("Genders:", len(genders))
    print("Actual observations:", len(values))

    print("\nOBSERVATION QUALITY BY YEAR")

    for year in years:

        year_values = []

        for region in regions:
            for age in ages:
                for gender in genders:

                    position = get_position(
                        region, age, gender, year
                    )

                    year_values.append(values[position])

        zero_count = sum(
            value == 0
            for value in year_values
            if value is not None
        )

        positive_count = sum(
            value > 0
            for value in year_values
            if value is not None
        )

        missing_count = sum(
            value is None
            for value in year_values
        )

        print(
            f"{year}: "
            f"Total={len(year_values)}, "
            f"Zero={zero_count}, "
            f"Positive={positive_count}, "
            f"Missing={missing_count}"
        )

    print("\nTOTAL POPULATION BY YEAR")
    print("(Gender: 1+2, Age: totalt)")

    for year in years:

        total_population = 0

        for region in regions:

            position = get_position(
                region=region,
                age="totalt",
                gender="1+2",
                year=year
            )

            value = values[position]

            if value is not None:
                total_population += value

        print(f"{year}: {total_population:,}")


def main():

    for name, file_path in FILES.items():
        profile_file(name, file_path)


if __name__ == "__main__":
    main()
