
import json
from pathlib import Path

TABLE1 = "TAB6471_20261026T133903Z.json"
TABLE2 = "TAB638_20261026T133900Z.json"

file_path = Path(f"data/raw/{TABLE1}")
data = json.loads(file_path.read_text(encoding="utf-8"))

print("Dataset:", data["label"])
print("Last updated:", data["updated"])
print("Dimensions:\n")

for dimension_name, dimension in data["dimension"].items():
    print(f"--- {dimension_name} ---")
    print("Label:", dimension.get("label"))
    print("Category index:", dimension.get("category", {}).get("index"))
    print("Category labels:", dimension.get("category", {}).get("label"))
    print()
