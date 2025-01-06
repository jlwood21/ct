import json
import os

from app.models import (
    Mission, Skill, Artifact,
    Reflection, Challenge, Profile
)

MISSIONS_FILE = "missions.json"
SKILLS_FILE = "skills.json"
ARTIFACTS_FILE = "artifacts.json"
REFLECTIONS_FILE = "reflections.json"
CHALLENGES_FILE = "challenges.json"
PROFILE_FILE = "profile.json"


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


# ------------------ REFLECTIONS (Step 34) --------------
# We'll store reflections as a dict: { "YYYY-MM-DD": "... content ..." }
def load_reflections() -> dict:
    if not os.path.exists(REFLECTIONS_FILE):
        return {}
    with open(REFLECTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_reflections(reflections: dict) -> None:
    with open(REFLECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(reflections, f, indent=2)


# ------------------ CHALLENGES (Step 36) --------------
def load_challenges() -> list[Challenge]:
    if not os.path.exists(CHALLENGES_FILE):
        return []
    with open(CHALLENGES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Challenge(**c) for c in data]

def save_challenges(challenges: list[Challenge]) -> None:
    data = [c.__dict__ for c in challenges]
    with open(CHALLENGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ------------------ PROFILE (Step 38) --------------
def load_profile() -> Profile | None:
    if not os.path.exists(PROFILE_FILE):
        return None
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return Profile(**data)

def save_profile(profile: Profile) -> None:
    data = profile.__dict__
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)