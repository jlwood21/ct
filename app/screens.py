from textual.screen import Screen
from textual.widgets import Static
from textual.app import ComposeResult
from textual.binding import Binding

import random
import datetime

from app.models import Mission, Skill, Artifact
from app.data_manager import (
    load_missions, save_missions,
    load_skills, save_skills,
    load_artifacts, save_artifacts
)
from app.settings_manager import load_settings, save_settings
from app.themes import THEMES

from textual.message import Message
from textual.reactive import var


# ------------ NOTIFICATION MESSAGES ------------
class MissionCompleted(Message):
    """Message posted when a mission is completed."""
    def __init__(self, sender, mission_title: str):
        super().__init__(sender)
        self.mission_title = mission_title

class SkillLeveledUp(Message):
    """Message posted when a skill is leveled up."""
    def __init__(self, sender, skill_name: str):
        super().__init__(sender)
        self.skill_name = skill_name

class ArtifactCollected(Message):
    """Message posted when an artifact is marked as collected."""
    def __init__(self, sender, artifact_name: str):
        super().__init__(sender)
        self.artifact_name = artifact_name


# ------------ TEMPLE GATE SCREEN ------------
class TempleGateScreen(Screen):
    """
    The main menu with options for Missions, Skill Trees, and Artifacts,
    plus a daily cosmic event display.
    """

    BINDINGS = [
        Binding("1", "goto_missions", "Go to Missions"),
        Binding("2", "goto_skill_trees", "Go to Skill Trees"),
        Binding("3", "goto_artifacts", "Go to Artifacts"),
        Binding("t", "cycle_theme", "Cycle Theme"),
        Binding("b", "pop_screen", "Go back"),
    ]

    cosmic_events = [
        "A solar flare ignites your determination.",
        "Cosmic winds blow fresh ideas your way.",
        "A meteor shower of creativity streaks across your mind.",
        "The alignment of distant stars fuels your ambition.",
    ]

    def compose(self) -> ComposeResult:
        menu_text = [
            "==========================",
            "     The Temple Gate     ",
            "==========================",
            "",
            " [1] Missions",
            " [2] Skill Trees",
            " [3] Artifacts",
            "",
            " [t] Cycle Theme",
            " [b] Go Back to Banner",
        ]
        yield Static("\n".join(menu_text), id="temple_gate_text")

    def on_mount(self) -> None:
        """Show daily cosmic event, style the gate text using app.cosmic_theme."""
        gate_text = self.query_one("#temple_gate_text", Static)
        app = self.app  # reference to CosmicTempleApp

        gate_text.styles.background = app.cosmic_theme["background"]
        gate_text.styles.color = app.cosmic_theme["foreground"]
        gate_text.styles.bold = True

        # Show cosmic event only once per day
        today_str = datetime.date.today().isoformat()
        settings = load_settings()
        last_date = settings.get("last_cosmic_event_date", None)

        if last_date != today_str:
            cosmic_event = random.choice(self.cosmic_events)
            old_content = gate_text.renderable
            new_content = f"**Cosmic Event [{today_str}]:** {cosmic_event}\n\n{old_content}"
            gate_text.update(new_content)

            settings["last_cosmic_event_date"] = today_str
            save_settings(settings)

    def action_goto_missions(self) -> None:
        self.app.push_screen(MissionsScreen())

    def action_goto_skill_trees(self) -> None:
        self.app.push_screen(SkillTreesScreen())

    def action_goto_artifacts(self) -> None:
        self.app.push_screen(ArtifactsScreen())

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_cycle_theme(self) -> None:
        """
        Cycle through available themes by updating app.current_theme_name
        and app.cosmic_theme, then re-render.
        """
        theme_names = list(THEMES.keys())
        current_index = theme_names.index(self.app.current_theme_name)
        next_index = (current_index + 1) % len(theme_names)
        next_theme_name = theme_names[next_index]

        self.app.set_theme(next_theme_name)
        # Force re-render of the screen so background/foreground updates
        self.refresh()
        self.on_mount()


# ------------ MISSIONS SCREEN ------------
class MissionsScreen(Screen):
    """
    Displays the user's missions with ability to toggle completion.
    """

    # We bind numeric keys to toggle missions
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("1", "toggle_mission(1)", "Toggle mission #1"),
        Binding("2", "toggle_mission(2)", "Toggle mission #2"),
        Binding("3", "toggle_mission(3)", "Toggle mission #3"),
        Binding("4", "toggle_mission(4)", "Toggle mission #4"),
        Binding("5", "toggle_mission(5)", "Toggle mission #5"),
        Binding("6", "toggle_mission(6)", "Toggle mission #6"),
        Binding("7", "toggle_mission(7)", "Toggle mission #7"),
        Binding("8", "toggle_mission(8)", "Toggle mission #8"),
        Binding("9", "toggle_mission(9)", "Toggle mission #9"),
    ]

    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.missions = load_missions()
        # If no data file existed, initialize with defaults
        if not self.missions:
            default_missions = [
                Mission("Stardust Fitness", "Run for 30 minutes"),
                Mission("Galaxy Brain Coding", "Complete a coding tutorial"),
                Mission("Astral Reading", "Read 20 pages of science/philosophy"),
            ]
            self.missions.extend(default_missions)
            save_missions(self.missions)

    def compose(self) -> ComposeResult:
        text_lines = [
            "****************************",
            "*       Missions List       *",
            "****************************",
            "",
        ]
        for i, mission in enumerate(self.missions, start=1):
            status = "[X]" if mission.completed else "[ ]"
            text_lines.append(f"{i}. {status} {mission.title} - {mission.description}")

        text_lines.append("\nPress [b] to go back.")
        text_lines.append("Press a number key (1-9) to toggle mission completion.")

        if self.notification:
            text_lines.append(f"\n[NOTIFICATION] {self.notification}")

        missions_text = "\n".join(text_lines)
        yield Static(missions_text, id="missions_text")

    def on_mount(self) -> None:
        app = self.app
        missions_text = self.query_one("#missions_text", Static)
        missions_text.styles.background = app.cosmic_theme["background"]
        missions_text.styles.color = app.cosmic_theme["foreground"]
        missions_text.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_toggle_mission(self, number: str) -> None:
        idx = int(number) - 1
        if 0 <= idx < len(self.missions):
            self.missions[idx].completed = not self.missions[idx].completed
            save_missions(self.missions)
            if self.missions[idx].completed:
                self.notification = f"Mission '{self.missions[idx].title}' completed!"
            else:
                self.notification = f"Mission '{self.missions[idx].title}' is pending now."
            self.refresh()


# ------------ SKILL TREES SCREEN ------------
class SkillTreesScreen(Screen):
    """
    Displays user's skill trees with ability to 'level up' a skill.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("1", "level_up_skill(1)", "Level up skill #1"),
        Binding("2", "level_up_skill(2)", "Level up skill #2"),
        Binding("3", "level_up_skill(3)", "Level up skill #3"),
        Binding("4", "level_up_skill(4)", "Level up skill #4"),
    ]

    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.skills = load_skills()
        # If none, initialize with defaults
        if not self.skills:
            default_skills = [
                Skill("Fitness", level=1, progress=20),
                Skill("Coding", level=2, progress=50),
                Skill("Writing", level=1, progress=10),
            ]
            self.skills.extend(default_skills)
            save_skills(self.skills)

    def compose(self) -> ComposeResult:
        text_lines = [
            "****************************",
            "*       Skill Trees        *",
            "****************************",
            "",
        ]
        for i, skill in enumerate(self.skills, start=1):
            text_lines.append(
                f"{i}. {skill.name} - Level {skill.level} ({skill.progress}% progress)"
            )

        text_lines.append("\nPress a number key (1-4) to level up a skill.")
        text_lines.append("Press [b] to go back.")

        if self.notification:
            text_lines.append(f"\n[NOTIFICATION] {self.notification}")

        yield Static("\n".join(text_lines), id="skill_trees_text")

    def on_mount(self) -> None:
        app = self.app
        st_text = self.query_one("#skill_trees_text", Static)
        st_text.styles.background = app.cosmic_theme["background"]
        st_text.styles.color = app.cosmic_theme["foreground"]
        st_text.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_level_up_skill(self, number: str) -> None:
        idx = int(number) - 1
        if 0 <= idx < len(self.skills):
            self.skills[idx].progress += 25
            if self.skills[idx].progress >= 100:
                self.skills[idx].level += 1
                self.skills[idx].progress = 0
                self.notification = f"Skill '{self.skills[idx].name}' leveled up!"
            else:
                self.notification = f"Skill '{self.skills[idx].name}' progress +25%"
            save_skills(self.skills)
            self.refresh()


# ------------ ARTIFACTS SCREEN ------------
class ArtifactsScreen(Screen):
    """
    Displays cosmic artifacts with ability to toggle 'collected'.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("1", "toggle_artifact(1)", "Toggle artifact #1"),
        Binding("2", "toggle_artifact(2)", "Toggle artifact #2"),
        Binding("3", "toggle_artifact(3)", "Toggle artifact #3"),
        Binding("4", "toggle_artifact(4)", "Toggle artifact #4"),
    ]

    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.artifacts = load_artifacts()
        # If none, initialize with defaults
        if not self.artifacts:
            default_artifacts = [
                Artifact("Nebula Shard", collected=False),
                Artifact("Meteor Fragment", collected=True),
                Artifact("Star Cluster", collected=False),
            ]
            self.artifacts.extend(default_artifacts)
            save_artifacts(self.artifacts)

    def compose(self) -> ComposeResult:
        text_lines = [
            "****************************",
            "*     Cosmic Artifacts     *",
            "****************************",
            "",
        ]
        for i, artifact in enumerate(self.artifacts, start=1):
            status = "[COLLECTED]" if artifact.collected else "[UNCOLLECTED]"
            text_lines.append(f"{i}. {status} {artifact.name}")

        text_lines.append("\nPress a number key (1-4) to toggle an artifact's status.")
        text_lines.append("Press [b] to go back.")

        if self.notification:
            text_lines.append(f"\n[NOTIFICATION] {self.notification}")

        yield Static("\n".join(text_lines), id="artifacts_text")

    def on_mount(self) -> None:
        app = self.app
        art_text = self.query_one("#artifacts_text", Static)
        art_text.styles.background = app.cosmic_theme["background"]
        art_text.styles.color = app.cosmic_theme["foreground"]
        art_text.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_toggle_artifact(self, number: str) -> None:
        idx = int(number) - 1
        if 0 <= idx < len(self.artifacts):
            self.artifacts[idx].collected = not self.artifacts[idx].collected
            if self.artifacts[idx].collected:
                self.notification = f"Artifact '{self.artifacts[idx].name}' is now collected!"
            else:
                self.notification = f"Artifact '{self.artifacts[idx].name}' is now uncollected."
            save_artifacts(self.artifacts)
            self.refresh()