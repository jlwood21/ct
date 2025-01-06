import json
import os

from app.models import (
    Mission, Skill, Artifact,
    Reflection, Challenge, Profile,
    Badge, Quest
)

MISSIONS_FILE = "missions.json"
SKILLS_FILE = "skills.json"
ARTIFACTS_FILE = "artifacts.json"
REFLECTIONS_FILE = "reflections.json"
CHALLENGES_FILE = "challenges.json"
PROFILE_FILE = "profile.json"
LORE_FILE = "lore.json"
ORACLES_FILE = "oracles.json"
BADGES_FILE = "badges.json"
QUESTS_FILE = "quests.json"
EXPORT_FILE = "export.json"

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


# ------------------ REFLECTIONS ----------------
def load_reflections() -> dict:
    if not os.path.exists(REFLECTIONS_FILE):
        return {}
    with open(REFLECTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_reflections(reflections: dict) -> None:
    with open(REFLECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(reflections, f, indent=2)


# ------------------ CHALLENGES ----------------
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


# ------------------ PROFILE -------------------
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


# ------------------ LORE & ORACLES -------------
def load_lore_snippets() -> list[str]:
    if not os.path.exists(LORE_FILE):
        return []
    with open(LORE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return []

def load_oracles() -> dict:
    if not os.path.exists(ORACLES_FILE):
        return {}
    with open(ORACLES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------ ACHIEVEMENTS (BADGES) ------
def load_achievements() -> list[Badge]:
    if not os.path.exists(BADGES_FILE):
        return []
    with open(BADGES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Badge(**b) for b in data]

def save_achievements(badges: list[Badge]) -> None:
    data = [b.__dict__ for b in badges]
    with open(BADGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ------------------ QUESTS ---------------------
def load_quests() -> list[Quest]:
    if not os.path.exists(QUESTS_FILE):
        return []
    with open(QUESTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Quest(**q) for q in data]

def save_quests(quests: list[Quest]) -> None:
    data = [q.__dict__ for q in quests]
    with open(QUESTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ------------------ OFFLINE EXPORT/IMPORT ------
def export_all_data() -> None:
    """Export Missions, Skills, Artifacts, Reflections, etc. to export.json."""
    export_data = {}

    # Missions
    missions = load_missions()
    export_data["missions"] = [m.__dict__ for m in missions]

    # Skills
    skills = load_skills()
    export_data["skills"] = [s.__dict__ for s in skills]

    # Artifacts
    artifacts = load_artifacts()
    export_data["artifacts"] = [a.__dict__ for a in artifacts]

    # Reflections
    reflections = load_reflections()
    export_data["reflections"] = reflections

    # Challenges
    challenges = load_challenges()
    export_data["challenges"] = [c.__dict__ for c in challenges]

    # Profile
    profile = load_profile()
    export_data["profile"] = profile.__dict__ if profile else {}

    # Achievements
    badges = load_achievements()
    export_data["badges"] = [b.__dict__ for b in badges]

    # Quests
    quests = load_quests()
    export_data["quests"] = [q.__dict__ for q in quests]

    with open("export.json", "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)


def import_all_data(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Missions
    if "missions" in data:
        missions = [Mission(**m) for m in data["missions"]]
        save_missions(missions)

    # Skills
    if "skills" in data:
        skills = [Skill(**s) for s in data["skills"]]
        save_skills(skills)

    # Artifacts
    if "artifacts" in data:
        artifacts = [Artifact(**a) for a in data["artifacts"]]
        save_artifacts(artifacts)

    # Reflections
    if "reflections" in data:
        save_reflections(data["reflections"])

    # Challenges
    if "challenges" in data:
        challenges = [Challenge(**c) for c in data["challenges"]]
        save_challenges(challenges)

    # Profile
    if "profile" in data:
        p = Profile(**data["profile"])
        save_profile(p)

    # Achievements
    if "badges" in data:
        badges = [Badge(**b) for b in data["badges"]]
        save_achievements(badges)

    # Quests
    if "quests" in data:
        quests = [Quest(**q) for q in data["quests"]]
        save_quests(quests)