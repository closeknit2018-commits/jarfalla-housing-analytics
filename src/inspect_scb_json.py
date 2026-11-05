
import json
from pathlib import Path

files = [
    Path("data/raw/TAB638_20261026T133900Z.json"),
    Path("data/raw/TAB6471_20261026T133903Z.json"),
]

for file_path in files:
    print(f"\n--- {file_path} ---")

    data = json.loads(file_path.read_text(encoding="utf-8"))

    print("Type:", type(data).__name__)

    if isinstance(data, dict):
        print("Keys:", list(data.keys()))

        for key, value in data.items():
            if isinstance(value, list):
                print(f"List '{key}': {len(value)} items")
                print("Sample:", value[:1])

            elif isinstance(value, dict):
                print(f"Dict '{key}' keys:", list(value.keys())[:10])

            else:
                print(f"{key} =", str(value)[:200])

    elif isinstance(data, list):
        print("Items:", len(data))
        print("Sample:", data[:1])
