
import csv
import json
from itertools import product
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
GOLD_DIR = PROJECT_DIR / "data" / "gold"
GOLD_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "TAB638": RAW_DIR / "TAB638_20261026T133900Z.json",
    "TAB6471": RAW_DIR / "TAB6471_20261026T133903Z.json",
    "DeSO2018": RAW_DIR / "scb_deso_population_2018.json",
    "DeSO2025": RAW_DIR / "scb_deso_population_2025.json",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_codes(data, dimension_id):
    """Return category codes in their original index order."""
    index = data["dimension"][dimension_id]["category"]["index"]
    return sorted(index, key=index.get)


def get_flat_index(data, selected_codes):
    """
    Convert dimension coordinates into a flat JSON-stat2 value index.
    selected_codes contains one category code for each dimension.
    """
    flat_index = 0

    for dimension_id, code in zip(data["id"], selected_codes):
        category_index = data["dimension"][dimension_id]["category"]["index"]
        position = category_index[code]
        dimension_size = data["size"][data["id"].index(dimension_id)]

        flat_index = flat_index * dimension_size + position

    return flat_index


def sum_population(data, filters):
    """
    Sum observations matching the supplied dimension filters.

    Dimensions not included in filters use all their categories.
    Returns the observed sum and the number of missing values.
    """
    dimensions = data["id"]
    values = data["value"]

    selected_codes = []

    for dimension_id in dimensions:
        available_codes = get_codes(data, dimension_id)

        if dimension_id in filters:
            allowed = set(filters[dimension_id])
            codes = [code for code in available_codes if code in allowed]

            if not codes:
                raise ValueError(
                    f"No matching codes for {dimension_id}: "
                    f"{filters[dimension_id]}"
                )
        else:
            codes = available_codes

        selected_codes.append(codes)

    total = 0
    missing_count = 0

    for combination in product(*selected_codes):
        flat_index = get_flat_index(data, combination)

        if isinstance(values, dict):
            value = values.get(str(flat_index))
        else:
            value = values[flat_index]

        if value is None:
            missing_count += 1
        else:
            total += value

    return total, missing_count


def calculate_tab638(data):
    """Calculate municipality population for each year."""
    years = get_codes(data, "Tid")

    civil_status = get_codes(data, "Civilstand")
    ages = get_codes(data, "Alder")
    genders = get_codes(data, "Kon")

    results = {}

    for year in years:
        total, missing = sum_population(
            data,
            {
                "Region": ["0123"],
                "Civilstand": civil_status,
                "Alder": ages,  # Includes 'us' if present
                "Kon": genders,
                "ContentsCode": ["BE0101N1"],
                "Tid": [year],
            },
        )

        results[year] = {
            "population": total,
            "missing": missing,
        }

    return results


def calculate_deso(data):
    """Calculate population by summing all DeSO regions."""
    years = get_codes(data, "Tid")

    results = {}

    for year in years:
        total, missing = sum_population(
            data,
            {
                "Alder": ["totalt"],
                "Kon": ["1+2"],
                "ContentsCode": ["000007Y7"],
                "Tid": [year],
            },
        )

        results[year] = {
            "population": total,
            "missing": missing,
        }

    return results


def calculate_tab6471(data):
    """Calculate municipality population for December 2025."""
    total, missing = sum_population(
        data,
        {
            "Region": ["0123"],
            "Alder": ["TotSA"],
            "Kon": ["1", "2"],
            "ContentsCode": ["000007SF"],
            "Tid": ["2025M12"],
        },
    )

    return {
        "population": total,
        "missing": missing,
    }


def compare(source_a, source_b):
    difference = source_a - source_b

    percentage = (
        difference / source_b * 100
        if source_b != 0
        else None
    )

    return difference, percentage


def main():
    print("Loading population data...")

    tab638 = load_json(FILES["TAB638"])
    tab6471 = load_json(FILES["TAB6471"])
    deso2018 = load_json(FILES["DeSO2018"])
    deso2025 = load_json(FILES["DeSO2025"])

    municipality_annual = calculate_tab638(tab638)
    municipality_2025 = calculate_tab6471(tab6471)

    old_deso = calculate_deso(deso2018)
    new_deso = calculate_deso(deso2025)

    rows = []

    # Compare 2010–2023: TAB638 vs DeSO 2018
    for year in sorted(set(municipality_annual) & set(old_deso)):
        if not 2010 <= int(year) <= 2023:
            continue

        municipality = municipality_annual[year]
        deso = old_deso[year]

        difference, percentage = compare(
            deso["population"],
            municipality["population"],
        )

        rows.append({
            "year": year,
            "comparison": "TAB638 vs DeSO2018",
            "municipality_population": municipality["population"],
            "deso_population": deso["population"],
            "difference": difference,
            "difference_percent": percentage,
            "municipality_missing": municipality["missing"],
            "deso_missing": deso["missing"],
        })

    # Compare 2024: TAB638 vs DeSO 2025
    municipality = municipality_annual["2024"]
    deso = new_deso["2024"]

    difference, percentage = compare(
        deso["population"],
        municipality["population"],
    )

    rows.append({
        "year": "2024",
        "comparison": "TAB638 vs DeSO2025",
        "municipality_population": municipality["population"],
        "deso_population": deso["population"],
        "difference": difference,
        "difference_percent": percentage,
        "municipality_missing": municipality["missing"],
        "deso_missing": deso["missing"],
    })

    # Compare 2025: TAB6471 vs DeSO 2025
    deso = new_deso["2025"]

    difference, percentage = compare(
        deso["population"],
        municipality_2025["population"],
    )

    rows.append({
        "year": "2025",
        "comparison": "TAB6471 vs DeSO2025",
        "municipality_population": municipality_2025["population"],
        "deso_population": deso["population"],
        "difference": difference,
        "difference_percent": percentage,
        "municipality_missing": municipality_2025["missing"],
        "deso_missing": deso["missing"],
    })

    output_file = GOLD_DIR / "population_validation.csv"

    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("\nPOPULATION VALIDATION")
    print("-" * 90)

    for row in rows:
        print(
            f"{row['year']} | {row['comparison']} | "
            f"Municipality: {row['municipality_population']:,} | "
            f"DeSO: {row['deso_population']:,} | "
            f"Difference: {row['difference']:+,} | "
            f"{row['difference_percent']:.4f}%"
            if row["difference_percent"] is not None
            else f"{row['year']} | Percentage unavailable"
        )

        if row["municipality_missing"] or row["deso_missing"]:
            print(
                "  Missing observations:",
                row["municipality_missing"],
                row["deso_missing"],
            )

    print(f"\nValidation report saved to: {output_file}")


if __name__ == "__main__":
    main()
