from pathlib import Path

folders = [
    "data/raw",
    "data/interim",
    "data/processed",
    "results",
    "notebooks",
]

for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

print("Project folders checked/created.")