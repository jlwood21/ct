import asyncio
import datetime
import random
import os

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
    load_profile, save_profile,
    load_lore_snippets, load_oracles
)
from app.settings_manager import load_settings, save_settings
from app.themes import THEMES


# -------------- ASCII FADE TRANSITION --------------
async def fade_transition(app):
    """
    A quick fade-like transition in ASCII to emulate
    old-school look, purely CPU-based, no GPU.
    """
    for _ in range(6):
        if random.random() < 0.5:
            app.console.print("\033[7m" + " " * 80 + "\033[0m")
        else:
            row = "".join(random.choice([" ", "*"]) for _ in range(60))
            app.console.print(row)
        await asyncio.sleep(0.05)


# -------------- HELPER: BEEP --------------
def beep():
    """
    Emit a console beep, if supported by the terminal.
    Alternatively, on macOS, you could do:
    os.system('afplay beep.wav')
    """
    print("\a")


# -------------- TEMPLE GATE SCREEN --------------
class TempleGateScreen(Screen):
    """
    Adds daily "Lore Snippets" and the regular nav.
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

        # Daily cosmic event snippet
        today_str = datetime.date.today().isoformat()
        settings = load_settings()
        last_date = settings.get("last_cosmic_event_date", None)

        if last_date != today_str:
            lore = load_lore_snippets()
            if lore:
                snippet = random.choice(lore)
                old_content = gate_text.renderable
                new_content = f"**Daily Lore [{today_str}]:** {snippet}\n\n{old_content}"
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


# -------------- MISSIONS SCREEN (Streak + Oracle) --------------
class MissionsScreen(Screen):
    """
    Displays the user's missions with ability to toggle completion,
    press 'o' for an oracle tip, track daily streak if at least 1 mission done.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("o", "oracle_tip", "Get Oracle Tip"),
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

        text_lines.append("\nPress [o] for an Oracle Tip. Press number keys (1-9) to toggle a mission. Press [b] to go back.")

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

    def action_oracle_tip(self) -> None:
        oracles = load_oracles()
        if oracles and "missions" in oracles:
            tip = random.choice(oracles["missions"])
            self.notification = f"Oracle says: {tip}"
        else:
            self.notification = "No oracles available for Missions!"
        self.refresh()

    def action_toggle_mission(self, number: str) -> None:
        idx = int(number) - 1
        if 0 <= idx < len(self.missions):
            self.missions[idx].completed = not self.missions[idx].completed
            save_missions(self.missions)

            # If completed, beep & set daily mission streak
            if self.missions[idx].completed:
                beep()
                self.notification = f"Mission '{self.missions[idx].title}' completed!"
                self.update_mission_streak()
            else:
                self.notification = f"Mission '{self.missions[idx].title}' is pending now."

            self.refresh()

    def update_mission_streak(self):
        # If user completes at least 1 mission on a given day, that day counts
        settings = load_settings()
        today = datetime.date.today().isoformat()
        last_mission_day = settings.get("last_mission_day", None)
        mission_streak = settings.get("mission_streak", 0)

        if last_mission_day == today:
            # Already counted a mission today
            pass
        else:
            # Next consecutive day or reset
            if last_mission_day is not None:
                # Check if yesterday was last day
                yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
                if yesterday == last_mission_day:
                    mission_streak += 1
                else:
                    mission_streak = 1
            else:
                mission_streak = 1

        settings["mission_streak"] = mission_streak
        settings["last_mission_day"] = today
        save_settings(settings)
        self.notification += f" (Mission Streak: {mission_streak} days)"


# -------------- SKILL TREES SCREEN (Beep on Level Up) --------------
class SkillTreesScreen(Screen):
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
            text_lines.append(f"{i}. {skill.name} - Level {skill.level} ({skill.progress}% progress)")

        text_lines.append("\nPress [1-4] to 'level up' a skill. [b] to go back.")

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
                beep()  # beep on level up
                self.notification = f"Skill '{self.skills[idx].name}' leveled up!"
            else:
                self.notification = f"Skill '{self.skills[idx].name}' progress +25%"
            save_skills(self.skills)
            self.refresh()


# -------------- ARTIFACTS SCREEN --------------
class ArtifactsScreen(Screen):
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

        text_lines.append("\nPress [1-4] to toggle an artifact. [b] to go back.")

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
                beep()
                self.notification = f"Artifact '{self.artifacts[idx].name}' is now collected!"
            else:
                self.notification = f"Artifact '{self.artifacts[idx].name}' is now uncollected."
            save_artifacts(self.artifacts)
            self.refresh()


# -------------- CREATIVE SANDBOX SCREEN --------------
class CreativeSandboxScreen(Screen):
    """
    Single-line input due to older Textual constraints. Press s to save, b to go back.
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

        self.input_widget = Input(
            placeholder="Type your cosmic ideas here...",
            id="sandbox_input"
        )
        yield self.input_widget

    def on_mount(self) -> None:
        app = self.app
        sandbox_header = self.query_one("#sandbox_header", Static)
        sandbox_header.styles.background = app.cosmic_theme["background"]
        sandbox_header.styles.color = app.cosmic_theme["foreground"]
        sandbox_header.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_save_content(self) -> None:
        content = self.input_widget.value
        with open("sandbox.txt", "w", encoding="utf-8") as f:
            f.write(content)
        self.query_one("#sandbox_header", Static).update(
            "Content saved to sandbox.txt!"
        )


# -------------- DAILY REFLECTION SCREEN (Streak logic) --------------
class ReflectionScreen(Screen):
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("r", "record_reflection", "Record Today's Reflection"),
    ]
    notification: var[str] = var("")

    def compose(self) -> ComposeResult:
        text_lines = [
            "****************************",
            "*     Daily Reflection     *",
            "****************************",
            "",
            "What went well today?",
            "What cosmic insight did you discover?",
            "Press [r] to record, [b] to go back."
        ]
        yield Static("\n".join(text_lines), id="reflection_header")

        self.reflection_input = Input(placeholder="Type your reflection here...", id="reflection_input")
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
            new_reflection_date = datetime.date.today().isoformat()
            reflections = load_reflections()
            reflections[new_reflection_date] = content
            save_reflections(reflections)
            self.notification = "Reflection saved!"
            # Update reflection streak
            self.update_reflection_streak()
        else:
            self.notification = "No content to save. Write something cosmic."
        self.refresh()

    def update_reflection_streak(self):
        settings = load_settings()
        today = datetime.date.today().isoformat()
        last_reflect_day = settings.get("last_reflect_day", None)
        reflect_streak = settings.get("reflect_streak", 0)

        if last_reflect_day == today:
            # Already reflected today
            pass
        else:
            # Next consecutive or reset
            if last_reflect_day is not None:
                yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
                if yesterday == last_reflect_day:
                    reflect_streak += 1
                else:
                    reflect_streak = 1
            else:
                reflect_streak = 1

        settings["reflect_streak"] = reflect_streak
        settings["last_reflect_day"] = today
        save_settings(settings)
        self.notification += f" (Reflection Streak: {reflect_streak} days)"


# -------------- COSMIC SCOREBOARD (Animated ASCII Constellation) --------------
class ScoreboardScreen(Screen):
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("c", "draw_constellation", "Animate Constellation"),
    ]
    notification: var[str] = var("")

    def compose(self) -> ComposeResult:
        text_lines = [
            "****************************",
            "*     Cosmic Scoreboard    *",
            "****************************",
            "",
        ]
        missions = load_missions()
        skills = load_skills()
        artifacts = load_artifacts()

        completed_missions = sum(1 for m in missions if m.completed)
        total_missions = len(missions)
        total_levels = sum(s.level for s in skills)
        collected_artifacts = sum(1 for a in artifacts if a.collected)
        total_artifacts = len(artifacts)

        text_lines.append(f"Missions Completed: {completed_missions}/{total_missions}")
        text_lines.append(f"Total Skill Levels Combined: {total_levels}")
        text_lines.append(f"Artifacts Collected: {collected_artifacts}/{total_artifacts}")

        # Also show streaks from settings
        settings = load_settings()
        mission_streak = settings.get("mission_streak", 0)
        reflect_streak = settings.get("reflect_streak", 0)
        text_lines.append(f"Mission Streak: {mission_streak} days")
        text_lines.append(f"Reflection Streak: {reflect_streak} days")

        text_lines.append("\nPress [c] to view a cosmic constellation animation. [b] to go back.")

        yield Static("\n".join(text_lines), id="scoreboard_text")

        # We'll also place a second widget for the constellation
        self.constellation_box = Static("", id="constellation_box")
        yield self.constellation_box

    def on_mount(self) -> None:
        sb_text = self.query_one("#scoreboard_text", Static)
        sb_text.styles.background = self.app.cosmic_theme["background"]
        sb_text.styles.color = self.app.cosmic_theme["foreground"]
        sb_text.styles.bold = True

        box = self.query_one("#constellation_box", Static)
        box.styles.background = self.app.cosmic_theme["background"]
        box.styles.color = self.app.cosmic_theme["foreground"]
        box.styles.bold = False

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    async def action_draw_constellation(self) -> None:
        # Simple ASCII star drawing
        box = self.query_one("#constellation_box", Static)
        lines = [
            "         *      .     ",
            "      .       *    .  ",
            "   *     .      *      ",
            "       .    *    .     ",
            "  .     *           *   ",
        ]
        rendered = ""
        for ln in lines:
            rendered += ln + "\n"
            box.update(rendered)
            await asyncio.sleep(0.3)

        # Optionally connect them with lines (just ASCII)
        connect_lines = [
            "         *------.     ",
            "      .------*    .   ",
            "   *----- .    -----  ",
        ]
        for ln in connect_lines:
            rendered += ln + "\n"
            box.update(rendered)
            await asyncio.sleep(0.3)


# -------------- CHALLENGES SCREEN (Temple Oracles) --------------
class ChallengesScreen(Screen):
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("n", "new_challenge", "New Challenge"),
        Binding("o", "oracle_tip", "Get Oracle Tip"),
        Binding("1", "toggle_challenge(1)", "Toggle challenge #1"),
        Binding("2", "toggle_challenge(2)", "Toggle challenge #2"),
        Binding("3", "toggle_challenge(3)", "Toggle challenge #3"),
    ]

    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.challenges = load_challenges()
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
            "Press [1-3] to increment progress or mark done.",
            "Press [o] for an Oracle Tip.",
        ]
        for i, ch in enumerate(self.challenges, start=1):
            deadline_str = ch.deadline
            progress_str = f"{ch.progress}/{ch.goal}"
            status = "DONE" if ch.progress >= ch.goal else "ONGOING"
            text_lines.append(f"{i}. {ch.title} | Deadline: {deadline_str} | Progress: {progress_str} ({status})")

        if self.notification:
            text_lines.append(f"\n[NOTIFICATION] {self.notification}")

        text_lines.append("\n[b] to go back.")
        yield Static("\n".join(text_lines), id="challenges_text")

    def on_mount(self) -> None:
        ch_text = self.query_one("#challenges_text", Static)
        ch_text.styles.background = self.app.cosmic_theme["background"]
        ch_text.styles.color = self.app.cosmic_theme["foreground"]
        ch_text.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_new_challenge(self) -> None:
        new_c = Challenge("New Challenge", (datetime.date.today() + datetime.timedelta(days=3)).isoformat(), 0, 3)
        self.challenges.append(new_c)
        save_challenges(self.challenges)
        self.notification = "Added a new challenge. Press number keys to increment progress."
        self.refresh()

    def action_toggle_challenge(self, number: str) -> None:
        idx = int(number) - 1
        if 0 <= idx < len(self.challenges):
            self.challenges[idx].progress += 1
            if self.challenges[idx].progress >= self.challenges[idx].goal:
                beep()
                self.notification = f"Challenge '{self.challenges[idx].title}' completed!"
            else:
                self.notification = f"Challenge '{self.challenges[idx].title}' progress {self.challenges[idx].progress}/{self.challenges[idx].goal}"
            save_challenges(self.challenges)
            self.refresh()

    def action_oracle_tip(self) -> None:
        oracles = load_oracles()
        if oracles and "challenges" in oracles:
            tip = random.choice(oracles["challenges"])
            self.notification = f"Oracle says: {tip}"
        else:
            self.notification = "No oracles available for Challenges!"
        self.refresh()


# -------------- PROFILE SCREEN (Titles / Avatars) --------------
class ProfileScreen(Screen):
    """
    Allows customizing user name, plus picking a cosmic title or avatar color.
    Press 'n' to cycle titles, 'a' to cycle avatar colors, 's' to save.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("n", "next_title", "Next Title"),
        Binding("a", "next_avatar", "Next Avatar"),
        Binding("s", "save_profile", "Save Profile"),
    ]

    titles = ["Stargazer", "Nova Runner", "Comet Shaman", "Celestial Alchemist"]
    avatar_colors = ["red", "green", "blue", "yellow", "magenta", "cyan", "white"]

    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.profile = load_profile()
        if not self.profile:
            # Default
            self.profile = Profile("Stargazer", title="Comet Shaman", avatar_color="white")
            save_profile(self.profile)

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*         Profile          *",
            "****************************",
            "",
            "Enter your cosmic moniker:",
            "Press [n] to cycle Title, [a] to cycle Avatar color, [s] to save, [b] to go back.",
        ]
        yield Static("\n".join(lines), id="profile_header")

        self.name_input = Input(placeholder="e.g. Nova Runner", id="profile_name_input")
        self.name_input.value = self.profile.name
        yield self.name_input

        self.title_static = Static(f"Title: {self.profile.title}", id="profile_title")
        yield self.title_static

        self.avatar_static = Static(f"Avatar Color: {self.profile.avatar_color}", id="profile_avatar")
        yield self.avatar_static

    def on_mount(self) -> None:
        ph = self.query_one("#profile_header", Static)
        ph.styles.background = self.app.cosmic_theme["background"]
        ph.styles.color = self.app.cosmic_theme["foreground"]
        ph.styles.bold = True

        self.query_one("#profile_title", Static).styles.background = self.app.cosmic_theme["background"]
        self.query_one("#profile_title", Static).styles.color = self.app.cosmic_theme["foreground"]
        self.query_one("#profile_avatar", Static).styles.background = self.app.cosmic_theme["background"]
        self.query_one("#profile_avatar", Static).styles.color = self.profile.avatar_color

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_next_title(self) -> None:
        idx = self.titles.index(self.profile.title) if self.profile.title in self.titles else 0
        idx = (idx + 1) % len(self.titles)
        self.profile.title = self.titles[idx]
        self.query_one("#profile_title", Static).update(f"Title: {self.profile.title}")

    def action_next_avatar(self) -> None:
        idx = self.avatar_colors.index(self.profile.avatar_color) if self.profile.avatar_color in self.avatar_colors else 0
        idx = (idx + 1) % len(self.avatar_colors)
        self.profile.avatar_color = self.avatar_colors[idx]
        self.query_one("#profile_avatar", Static).styles.color = self.profile.avatar_color
        self.query_one("#profile_avatar", Static).update(f"Avatar Color: {self.profile.avatar_color}")

    def action_save_profile(self) -> None:
        name = self.name_input.value.strip()
        if name:
            self.profile.name = name
            save_profile(self.profile)
            self.notification = f"Profile saved! Greetings, {self.profile.name} the {self.profile.title}."
        else:
            self.notification = "Please enter a valid name."

        header = self.query_one("#profile_header", Static)
        header.update(f"Profile: {self.notification}")
        self.refresh()