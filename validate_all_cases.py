import os
import json
from app.library.case_validator import validate_case

base_dir = r"c:\Users\Piyus\OneDrive\Desktop\Niet Workshop\AI_Mystery_Detective_Team\backend\src\cases"

cases = []
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == "case.json":
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                cases.append(json.load(f))

cases.sort(key=lambda c: c.get("caseId", ""))
print(f"Found {len(cases)} cases in backend/src/cases/")

all_valid = True
for c in cases:
    res = validate_case(c)
    print(f"{c.get('caseId')}: {c.get('title')} -> Valid: {res['valid']}")
    if not res["valid"]:
        all_valid = False
        print(f"  Errors: {res['errors']}")

print(f"\nFinal Result -> All 12 Cases Valid: {all_valid}")
