import json
import os
from app.models import Mission, Skill, Artifact

MISSIONS_FILE = "missions.json"
SKILLS_FILE = "skills.json"
ARTIFACTS_FILE = "artifacts.json"


# ------------------ MISSIONS ------------------
def load_missions() -> list[Mission]:
    if not os.path.exists(MISSIONS_FILE):
        return []
    with open(MISSIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Mission(**m) for m in data]

def save_missions(missions: list[Mission]) -> None:
    data = [m.__dict__ for m in missions]
    with open(MISSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ------------------ SKILLS --------------------
def load_skills() -> list[Skill]:
    if not os.path.exists(SKILLS_FILE):
        return []
    with open(SKILLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Skill(**s) for s in data]

def save_skills(skills: list[Skill]) -> None:
    data = [s.__dict__ for s in skills]
    with open(SKILLS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ------------------ ARTIFACTS -----------------
def load_artifacts() -> list[Artifact]:
    if not os.path.exists(ARTIFACTS_FILE):
        return []
    with open(ARTIFACTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Artifact(**a) for a in data]

def save_artifacts(artifacts: list[Artifact]) -> None:
    data = [a.__dict__ for a in artifacts]
    with open(ARTIFACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
