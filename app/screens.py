import asyncio
import datetime
import random

from textual.screen import Screen
from textual.widgets import Static, Input
from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import var

from app.models import (
    Mission, Skill, Artifact,
    Reflection, Challenge, Profile
)
from app.data_manager import (
    load_missions, save_missions,
    load_skills, save_skills,
    load_artifacts, save_artifacts,
    load_reflections, save_reflections,
    load_challenges, save_challenges,
    load_profile, save_profile
)
from app.settings_manager import load_settings, save_settings
from app.themes import THEMES

# -------------- ASCII FADE TRANSITION --------------
async def fade_transition(app):
    """
    A quick fade-like transition in ASCII to emulate
    old-school look, purely CPU-based, no GPU.
    """
    # We'll invert the screen a few times or print random stars, etc.
    for i in range(6):
        # Invert or random star
        if i % 2 == 0:
            app.console.print("\033[7m" + " " * 80 + "\033[0m")  # invert one line
        else:
            row = "".join(random.choice([" ", "*"]) for _ in range(60))
            app.console.print(row)
        await asyncio.sleep(0.05)

# -------------- TEMPLE GATE SCREEN --------------
class TempleGateScreen(Screen):
    """
    The main menu with options for Missions, Skill Trees, Artifacts,
    plus the new features: Creative Sandbox, Daily Reflection, Scoreboard, Challenges, Profile.
    """

    BINDINGS = [
        Binding("1", "goto_missions", "Go to Missions"),
        Binding("2", "goto_skill_trees", "Go to Skill Trees"),
        Binding("3", "goto_artifacts", "Go to Artifacts"),
        Binding("4", "goto_sandbox", "Creative Sandbox"),
        Binding("5", "goto_reflection", "Daily Reflection"),
        Binding("6", "goto_scoreboard", "Cosmic Scoreboard"),
        Binding("7", "goto_challenges", "Challenges"),
        Binding("8", "goto_profile", "Profile"),
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
            " [4] Creative Sandbox",
            " [5] Daily Reflection",
            " [6] Cosmic Scoreboard",
            " [7] Challenges",
            " [8] Profile",
            "",
            " [t] Cycle Theme",
            " [b] Go Back to Banner",
        ]
        yield Static("\n".join(menu_text), id="temple_gate_text")

    def on_mount(self) -> None:
        gate_text = self.query_one("#temple_gate_text", Static)
        app = self.app

        gate_text.styles.background = app.cosmic_theme["background"]
        gate_text.styles.color = app.cosmic_theme["foreground"]
        gate_text.styles.bold = True

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

    async def action_goto_missions(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(MissionsScreen())

    async def action_goto_skill_trees(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(SkillTreesScreen())

    async def action_goto_artifacts(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(ArtifactsScreen())

    async def action_goto_sandbox(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(CreativeSandboxScreen())

    async def action_goto_reflection(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(ReflectionScreen())

    async def action_goto_scoreboard(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(ScoreboardScreen())

    async def action_goto_challenges(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(ChallengesScreen())

    async def action_goto_profile(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(ProfileScreen())

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_cycle_theme(self) -> None:
        theme_names = list(THEMES.keys())
        current_index = theme_names.index(self.app.current_theme_name)
        next_index = (current_index + 1) % len(theme_names)
        next_theme_name = theme_names[next_index]

        self.app.set_theme(next_theme_name)
        self.refresh()
        self.on_mount()


# -------------- MISSIONS SCREEN --------------
class MissionsScreen(Screen):
    """
    Displays the user's missions with ability to toggle completion.
    """
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


# -------------- SKILL TREES SCREEN --------------
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


# -------------- ARTIFACTS SCREEN --------------
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


# -------------- CREATIVE SANDBOX SCREEN (Step 32) --------------
class CreativeSandboxScreen(Screen):
    """
    A free-form text area for brainstorming or journaling.
    No networking or AI calls (step 33 is skipped).
    Press s to save content, b to go back.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("s", "save_content", "Save Sandbox Content"),
    ]

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*    Creative Sandbox      *",
            "****************************",
            "\nType your ideas below. Press [s] to save, [b] to go back.",
        ]
        yield Static("\n".join(lines), id="sandbox_header")

        # Multi-line text input
        self.input_widget = Input(placeholder="Type your cosmic ideas here...", id="sandbox_input", multiline=True)
        yield self.input_widget

    def on_mount(self) -> None:
        app = self.app
        sandbox_header = self.query_one("#sandbox_header", Static)
        sandbox_header.styles.background = app.cosmic_theme["background"]
        sandbox_header.styles.color = app.cosmic_theme["foreground"]
        sandbox_header.styles.bold = True

        # We can load existing content from a file, if desired (optional).
        # For now, we won't store it permanently unless user saves manually.

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_save_content(self) -> None:
        content = self.input_widget.value
        # Save to a local file, e.g. "sandbox.txt"
        with open("sandbox.txt", "w", encoding="utf-8") as f:
            f.write(content)
        # We can display a small success message in the console or refresh the UI
        self.query_one("#sandbox_header", Static).update("Content saved to sandbox.txt!")


# -------------- DAILY REFLECTION SCREEN (Step 34) --------------
class ReflectionScreen(Screen):
    """
    A screen for daily reflections. Stores a reflection in reflections.json
    keyed by date. Press r to record, b to go back.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("r", "record_reflection", "Record Today's Reflection"),
    ]

    def compose(self) -> ComposeResult:
        text_lines = [
            "****************************",
            "*     Daily Reflection     *",
            "****************************",
            "",
            "What went well today?",
            "What cosmic insight did you discover?",
            "Press [r] when done, [b] to go back."
        ]
        yield Static("\n".join(text_lines), id="reflection_header")

        self.reflection_input = Input(placeholder="Type your reflection here...", multiline=True, id="reflection_input")
        yield self.reflection_input

    def on_mount(self) -> None:
        app = self.app
        rh = self.query_one("#reflection_header", Static)
        rh.styles.background = app.cosmic_theme["background"]
        rh.styles.color = app.cosmic_theme["foreground"]
        rh.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_record_reflection(self) -> None:
        content = self.reflection_input.value.strip()
        if content:
            new_reflection = Reflection(datetime.date.today().isoformat(), content)
            reflections = load_reflections()
            # Overwrite any existing reflection for the day
            # Or you could append if you wanted multiple entries
            # For now, let's do a simple dictionary approach
            # We'll see in data_manager
            reflections[new_reflection.date] = new_reflection.content
            save_reflections(reflections)
            self.query_one("#reflection_header", Static).update("Reflection saved!")
        else:
            self.query_one("#reflection_header", Static).update("No content to save. Write something cosmic.")


# -------------- COSMIC SCOREBOARD SCREEN (Step 35) --------------
class ScoreboardScreen(Screen):
    """
    Shows daily/weekly stats: how many Missions completed, Skills leveled, etc.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
    ]

    def compose(self) -> ComposeResult:
        text_lines = [
            "****************************",
            "*     Cosmic Scoreboard    *",
            "****************************",
            "",
        ]
        # We'll gather data from missions, skills, artifacts
        missions = load_missions()
        skills = load_skills()
        artifacts = load_artifacts()

        # Basic stats
        completed_missions = sum(1 for m in missions if m.completed)
        total_missions = len(missions)

        # Count how many skill level ups in total or how many are above level 1
        total_levels = sum(s.level for s in skills)

        # Count how many artifacts are collected
        collected_artifacts = sum(1 for a in artifacts if a.collected)
        total_artifacts = len(artifacts)

        text_lines.append(f"Missions Completed: {completed_missions}/{total_missions}")
        text_lines.append(f"Total Skill Levels Combined: {total_levels}")
        text_lines.append(f"Artifacts Collected: {collected_artifacts}/{total_artifacts}")

        text_lines.append("\nPress [b] to go back.")

        yield Static("\n".join(text_lines), id="scoreboard_text")

    def on_mount(self) -> None:
        app = self.app
        sb_text = self.query_one("#scoreboard_text", Static)
        sb_text.styles.background = app.cosmic_theme["background"]
        sb_text.styles.color = app.cosmic_theme["foreground"]
        sb_text.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()


# -------------- CHALLENGES SCREEN (Step 36) --------------
class ChallengesScreen(Screen):
    """
    Shows limited-time challenges: e.g., 'Complete 3 Missions in 2 days.'
    The user can create new challenges or mark them as done. 
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("n", "new_challenge", "New Challenge"),
        Binding("1", "toggle_challenge(1)", "Toggle challenge #1"),
        Binding("2", "toggle_challenge(2)", "Toggle challenge #2"),
        Binding("3", "toggle_challenge(3)", "Toggle challenge #3"),
    ]

    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.challenges = load_challenges()
        # If no data, we might create a default challenge
        if not self.challenges:
            example = Challenge("Complete 2 Missions", (datetime.date.today() + datetime.timedelta(days=2)).isoformat(), 0, 2)
            self.challenges.append(example)
            save_challenges(self.challenges)

    def compose(self) -> ComposeResult:
        text_lines = [
            "****************************",
            "*       Challenges         *",
            "****************************",
            "",
            "Press [n] to add a new challenge.",
            "Press [1], [2], [3]... to increment progress or mark done.",
        ]
        for i, ch in enumerate(self.challenges, start=1):
            deadline_str = ch.deadline
            progress_str = f"{ch.progress}/{ch.goal}"
            status = "DONE" if ch.progress >= ch.goal else "ONGOING"
            text_lines.append(f"{i}. {ch.title} | Deadline: {deadline_str} | Progress: {progress_str} ({status})")

        if self.notification:
            text_lines.append(f"\n[NOTIFICATION] {self.notification}")

        text_lines.append("\nPress [b] to go back.")
        yield Static("\n".join(text_lines), id="challenges_text")

    def on_mount(self) -> None:
        app = self.app
        ch_text = self.query_one("#challenges_text", Static)
        ch_text.styles.background = app.cosmic_theme["background"]
        ch_text.styles.color = app.cosmic_theme["foreground"]
        ch_text.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_toggle_challenge(self, number: str) -> None:
        idx = int(number) - 1
        if 0 <= idx < len(self.challenges):
            # Increment progress by 1 for demonstration
            self.challenges[idx].progress += 1
            if self.challenges[idx].progress >= self.challenges[idx].goal:
                self.notification = f"Challenge '{self.challenges[idx].title}' completed!"
            else:
                self.notification = f"Challenge '{self.challenges[idx].title}' progress {self.challenges[idx].progress}/{self.challenges[idx].goal}"
            save_challenges(self.challenges)
            self.refresh()

    def action_new_challenge(self) -> None:
        # Minimal: create a new challenge with placeholder
        new_c = Challenge("New Challenge", (datetime.date.today() + datetime.timedelta(days=3)).isoformat(), 0, 3)
        self.challenges.append(new_c)
        save_challenges(self.challenges)
        self.notification = "Added a new challenge (placeholder). Press number keys to increment progress."
        self.refresh()


# -------------- PROFILE SCREEN (Step 38) --------------
class ProfileScreen(Screen):
    """
    Allows customizing user name (cosmic moniker), stored in profile.json.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("s", "save_profile", "Save Profile"),
    ]

    def __init__(self):
        super().__init__()
        self.profile = load_profile()
        if not self.profile:
            # Default
            self.profile = Profile("Stargazer")  # default name
            save_profile(self.profile)

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*         Profile          *",
            "****************************",
            "",
            "Enter your cosmic moniker:",
            "Press [s] to save, [b] to go back.",
        ]
        yield Static("\n".join(lines), id="profile_header")

        self.name_input = Input(placeholder="e.g. Nova Runner", id="profile_name_input")
        # Prefill with existing name
        self.name_input.value = self.profile.name
        yield self.name_input

    def on_mount(self) -> None:
        app = self.app
        ph = self.query_one("#profile_header", Static)
        ph.styles.background = app.cosmic_theme["background"]
        ph.styles.color = app.cosmic_theme["foreground"]
        ph.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_save_profile(self) -> None:
        name = self.name_input.value.strip()
        if name:
            self.profile.name = name
            save_profile(self.profile)
            self.query_one("#profile_header", Static).update(f"Profile saved! Greetings, {name}.")
        else:
            self.query_one("#profile_header", Static).update("Please enter a valid name.")