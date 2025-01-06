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
    Reflection, Challenge, Profile,
    Badge, Quest
)
from app.data_manager import (
    load_missions, save_missions,
    load_skills, save_skills,
    load_artifacts, save_artifacts,
    load_reflections, save_reflections,
    load_challenges, save_challenges,
    load_profile, save_profile,
    load_lore_snippets, load_oracles,
    load_achievements, save_achievements,
    load_quests, save_quests,
    export_all_data, import_all_data
)
from app.settings_manager import load_settings, save_settings
from app.themes import THEMES


# -------------- ASCII FADE TRANSITION --------------
async def fade_transition(app):
    """A quick fade-like transition in ASCII to emulate old-school look."""
    for _ in range(6):
        if random.random() < 0.5:
            app.console.print("\033[7m" + " " * 80 + "\033[0m")
        else:
            row = "".join(random.choice([" ", "*"]) for _ in range(60))
            app.console.print(row)
        await asyncio.sleep(0.05)


# -------------- HELPER: BEEP --------------
def beep():
    """Simple console beep."""
    print("\a")


# -------------- TEMPLE GATE SCREEN --------------
class TempleGateScreen(Screen):
    """
    Main menu with daily lore, extended nav to new features:
    - (9) Time Machine
    - (0) Achievements
    - (q) Quests
    - (x) Export/Import
    - (p) Pilgrimage
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
        Binding("9", "goto_time_machine", "Time Machine"),
        Binding("0", "goto_achievements", "Achievements"),
        Binding("q", "goto_quests", "Cosmic Quests"),
        Binding("c", "goto_crafts", "Cosmic Crafts"),
        Binding("x", "goto_export_import", "Export/Import"),
        Binding("p", "goto_pilgrimage", "Temple Pilgrimage"),
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
            " [9] Time Machine",
            " [0] Achievements",
            " [q] Quests",
            " [c] Cosmic Crafts",
            " [x] Export/Import",
            " [p] Temple Pilgrimage",
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

        # Show daily lore snippet
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

    async def action_goto_time_machine(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(TimeMachineScreen())

    async def action_goto_achievements(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(AchievementsScreen())

    async def action_goto_quests(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(QuestsScreen())

    async def action_goto_crafts(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(CosmicCraftsScreen())

    async def action_goto_export_import(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(ExportImportScreen())

    async def action_goto_pilgrimage(self) -> None:
        await fade_transition(self.app)
        self.app.push_screen(TemplePilgrimageScreen())

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
    Missions, with daily streak, oracles, beep on completion.
    """
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("o", "oracle_tip", "Get Oracle Tip"),
        Binding("1", "toggle_mission(1)", "Toggle mission #1"),
        # ... up to 9 ...
        Binding("2", "toggle_mission(2)", ""),
        Binding("3", "toggle_mission(3)", ""),
        Binding("4", "toggle_mission(4)", ""),
        Binding("5", "toggle_mission(5)", ""),
        Binding("6", "toggle_mission(6)", ""),
        Binding("7", "toggle_mission(7)", ""),
        Binding("8", "toggle_mission(8)", ""),
        Binding("9", "toggle_mission(9)", ""),
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

        text_lines.append("\nPress (o) for an Oracle Tip. Number keys to toggle. (b) to go back.")
        if self.notification:
            text_lines.append(f"\n[NOTIFICATION] {self.notification}")

        yield Static("\n".join(text_lines), id="missions_text")

    def on_mount(self) -> None:
        missions_text = self.query_one("#missions_text", Static)
        missions_text.styles.background = self.app.cosmic_theme["background"]
        missions_text.styles.color = self.app.cosmic_theme["foreground"]
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

            if self.missions[idx].completed:
                beep()
                self.notification = f"Mission '{self.missions[idx].title}' completed!"
                self.update_mission_streak()
            else:
                self.notification = f"Mission '{self.missions[idx].title}' is pending now."
            self.refresh()

    def update_mission_streak(self):
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


# -------------- SKILL TREES SCREEN --------------
class SkillTreesScreen(Screen):
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("1", "level_up_skill(1)", "Level up #1"),
        Binding("2", "level_up_skill(2)", ""),
        Binding("3", "level_up_skill(3)", ""),
        Binding("4", "level_up_skill(4)", ""),
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
        lines = [
            "****************************",
            "*       Skill Trees        *",
            "****************************",
            "",
        ]
        for i, skill in enumerate(self.skills, start=1):
            lines.append(f"{i}. {skill.name} - L{skill.level} ({skill.progress}%)")

        lines.append("\nPress number keys to level up. (b) to go back.")
        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")

        yield Static("\n".join(lines), id="skill_trees_text")

    def on_mount(self) -> None:
        st_text = self.query_one("#skill_trees_text", Static)
        st_text.styles.background = self.app.cosmic_theme["background"]
        st_text.styles.color = self.app.cosmic_theme["foreground"]
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
                beep()
                self.notification = f"Skill '{self.skills[idx].name}' leveled up!"
            else:
                self.notification = f"Skill '{self.skills[idx].name}' progress +25%"
            save_skills(self.skills)
            self.refresh()


# -------------- ARTIFACTS SCREEN --------------
class ArtifactsScreen(Screen):
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("1", "toggle_artifact(1)", ""),
        Binding("2", "toggle_artifact(2)", ""),
        Binding("3", "toggle_artifact(3)", ""),
        Binding("4", "toggle_artifact(4)", ""),
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
        lines = [
            "****************************",
            "*     Cosmic Artifacts     *",
            "****************************",
            "",
        ]
        for i, artifact in enumerate(self.artifacts, start=1):
            status = "[COLLECTED]" if artifact.collected else "[UNCOLLECTED]"
            lines.append(f"{i}. {status} {artifact.name}")

        lines.append("\nPress number keys to toggle. (b) to go back.")
        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")

        yield Static("\n".join(lines), id="artifacts_text")

    def on_mount(self) -> None:
        art_text = self.query_one("#artifacts_text", Static)
        art_text.styles.background = self.app.cosmic_theme["background"]
        art_text.styles.color = self.app.cosmic_theme["foreground"]
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


# -------------- CREATIVE SANDBOX SCREEN (with ESC & Markov) --------------
class CreativeSandboxScreen(Screen):
    """
    Single-line input. (s) to save, (b) to go back, (g) to generate Markov suggestion, ESC to unfocus.
    We'll store lines in sandbox_lines.json, build a tiny Markov chain offline.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("s", "save_content", "Save Sandbox Content"),
        Binding("g", "gen_markov", "Generate Markov Suggestion"),
        Binding("escape", "exit_input_mode", "Exit Input"),
    ]

    notification: var[str] = var("")

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*    Creative Sandbox      *",
            "****************************",
            "\nType your ideas below. Press (s) to save, (g) for AI suggestion, (b) to go back. ESC to exit typing mode.",
        ]
        yield Static("\n".join(lines), id="sandbox_header")

        self.input_widget = Input(
            placeholder="Type your cosmic ideas here...",
            id="sandbox_input"
        )
        yield self.input_widget

    def on_mount(self) -> None:
        sb_header = self.query_one("#sandbox_header", Static)
        sb_header.styles.background = self.app.cosmic_theme["background"]
        sb_header.styles.color = self.app.cosmic_theme["foreground"]
        sb_header.styles.bold = True

        # Auto-focus input so user can type
        self.set_focus(self.input_widget)

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_exit_input_mode(self) -> None:
        """Unfocus input so 's','b','g' keys are recognized as commands."""
        self.set_focus(None)

    def action_save_content(self) -> None:
        content = self.input_widget.value.strip()
        if not content:
            self.notification = "No content to save."
        else:
            # Save to 'sandbox.txt'
            with open("sandbox.txt", "a", encoding="utf-8") as f:
                f.write(content + "\n")

            # Also store lines for Markov
            from app.sandbox_markov import add_sandbox_line
            add_sandbox_line(content)

            self.notification = "Content saved to sandbox.txt!"
            self.input_widget.value = ""  # clear input

        self.refresh()

    def action_gen_markov(self) -> None:
        """Generate a line via local Markov approach."""
        from app.sandbox_markov import generate_markov_line
        suggestion = generate_markov_line()
        if suggestion:
            self.notification = f"Markov suggests: '{suggestion}'"
        else:
            self.notification = "No Markov data yet. Add more lines first."
        self.refresh()

    def compose_notification_text(self) -> str:
        return f"\n[NOTIFICATION] {self.notification}" if self.notification else ""

    def refresh(self):
        sb_header = self.query_one("#sandbox_header", Static)
        lines = sb_header.renderable.split("\n")
        # Re-inject notification at the end
        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")
        sb_header.update("\n".join(lines))


# -------------- DAILY REFLECTION SCREEN --------------
class ReflectionScreen(Screen):
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("r", "record_reflection", "Record Reflection"),
    ]
    notification: var[str] = var("")

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*     Daily Reflection     *",
            "****************************",
            "",
            "What went well today?",
            "Press (r) to record, (b) to go back. ESC to exit input mode.",
        ]
        yield Static("\n".join(lines), id="reflection_header")

        self.reflection_input = Input(placeholder="Type your reflection here...", id="reflection_input")
        yield self.reflection_input

    def on_mount(self) -> None:
        rh = self.query_one("#reflection_header", Static)
        rh.styles.background = self.app.cosmic_theme["background"]
        rh.styles.color = self.app.cosmic_theme["foreground"]
        rh.styles.bold = True

        self.set_focus(self.reflection_input)

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
            self.update_reflection_streak()
            self.reflection_input.value = ""
        else:
            self.notification = "No content to save."
        self.refresh()

    def update_reflection_streak(self):
        settings = load_settings()
        today = datetime.date.today().isoformat()
        last_reflect_day = settings.get("last_reflect_day", None)
        reflect_streak = settings.get("reflect_streak", 0)

        if last_reflect_day == today:
            pass
        else:
            if last_reflect_day:
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

    def refresh(self):
        header = self.query_one("#reflection_header", Static)
        lines = header.renderable.split("\n")
        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")
        header.update("\n".join(lines))


# -------------- COSMIC SCOREBOARD (Existing) --------------
class ScoreboardScreen(Screen):
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("c", "draw_constellation", "Constellation"),
    ]
    notification: var[str] = var("")

    def compose(self) -> ComposeResult:
        lines = [
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

        settings = load_settings()
        mission_streak = settings.get("mission_streak", 0)
        reflect_streak = settings.get("reflect_streak", 0)

        lines.append(f"Missions Completed: {completed_missions}/{total_missions}")
        lines.append(f"Total Skill Levels: {total_levels}")
        lines.append(f"Artifacts Collected: {collected_artifacts}/{total_artifacts}")
        lines.append(f"Mission Streak: {mission_streak} days")
        lines.append(f"Reflection Streak: {reflect_streak} days")

        lines.append("\nPress (c) for cosmic constellation, (b) to go back.")
        yield Static("\n".join(lines), id="scoreboard_text")

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

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    async def action_draw_constellation(self) -> None:
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

        connect_lines = [
            "         *------.     ",
            "      .------*    .   ",
            "   *----- .    -----  ",
        ]
        for ln in connect_lines:
            rendered += ln + "\n"
            box.update(rendered)
            await asyncio.sleep(0.3)


# -------------- CHALLENGES SCREEN --------------
class ChallengesScreen(Screen):
    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("n", "new_challenge", "New Challenge"),
        Binding("o", "oracle_tip", "Oracle Tip"),
        Binding("1", "toggle_challenge(1)", ""),
        Binding("2", "toggle_challenge(2)", ""),
        Binding("3", "toggle_challenge(3)", ""),
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
        lines = [
            "****************************",
            "*       Challenges         *",
            "****************************",
            "",
            "Press (n) for new challenge, (o) for Oracle. Number keys to increment progress.",
        ]
        for i, ch in enumerate(self.challenges, start=1):
            status = "DONE" if ch.progress >= ch.goal else "ONGOING"
            lines.append(f"{i}. {ch.title} | {ch.progress}/{ch.goal} (Deadline: {ch.deadline}, {status})")

        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")
        lines.append("\n(b) to go back.")
        yield Static("\n".join(lines), id="challenges_text")

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
        self.notification = "Added a new challenge."
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
            self.notification = "No oracles for Challenges!"
        self.refresh()

    def refresh(self):
        ch_text = self.query_one("#challenges_text", Static)
        # Re-render
        self.compose()
        # Or do a small manual approach (omitted for brevity).


# -------------- PROFILE SCREEN --------------
class ProfileScreen(Screen):
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
            self.profile = Profile("Stargazer", title="Comet Shaman", avatar_color="white")
            save_profile(self.profile)

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*         Profile          *",
            "****************************",
            "",
            "Enter your cosmic moniker:",
            "(n) cycle title, (a) cycle avatar, (s) to save, (b) back.",
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
            self.notification = f"Saved! Hello, {self.profile.name} the {self.profile.title}."
        else:
            self.notification = "Please enter a valid name."

        hdr = self.query_one("#profile_header", Static)
        lines = hdr.renderable.split("\n")
        lines.append(f"\n[NOTIFICATION] {self.notification}")
        hdr.update("\n".join(lines))


# -------------- STEP 46: TIME MACHINE SCREEN --------------
class TimeMachineScreen(Screen):
    """
    Shows past reflections & completed missions by date.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
    ]

    def __init__(self):
        super().__init__()
        self.reflections = load_reflections()
        self.missions = load_missions()

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*       Time Machine       *",
            "****************************",
            "",
            "Review Past Reflections & Missions"
        ]
        # Show reflections by date
        for date_str, text in sorted(self.reflections.items()):
            lines.append(f"\n{date_str} Reflection: {text}")

        # Show completed missions by date? 
        # We might store mission completions in the future. For now, just list which are completed:
        completed = [m.title for m in self.missions if m.completed]
        lines.append("\nCompleted Missions:")
        if completed:
            for c in completed:
                lines.append(f" - {c}")
        else:
            lines.append(" None yet.")

        lines.append("\n(b) to go back.")
        yield Static("\n".join(lines), id="time_machine_text")

    def on_mount(self) -> None:
        tm_text = self.query_one("#time_machine_text", Static)
        tm_text.styles.background = self.app.cosmic_theme["background"]
        tm_text.styles.color = self.app.cosmic_theme["foreground"]
        tm_text.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()


# -------------- STEP 47: ACHIEVEMENTS SCREEN --------------
class AchievementsScreen(Screen):
    """
    List badges or milestone achievements. 
    Example: 10 Missions, 3 Artifacts, etc.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
    ]
    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.badges = load_achievements()

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*     Achievements (Badges) *",
            "****************************",
            ""
        ]
        if not self.badges:
            lines.append("No badges unlocked yet.")
        else:
            for badge in self.badges:
                lines.append(f"- {badge.title}: {badge.description}")

        lines.append("\n(b) to go back.")
        yield Static("\n".join(lines), id="achievements_text")

    def on_mount(self) -> None:
        ach_text = self.query_one("#achievements_text", Static)
        ach_text.styles.background = self.app.cosmic_theme["background"]
        ach_text.styles.color = self.app.cosmic_theme["foreground"]
        ach_text.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()


# -------------- STEP 48: COSMIC QUESTS SCREEN --------------
class QuestsScreen(Screen):
    """
    Themed, narrative-driven mission sets. 
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("1", "start_quest(1)", ""),
        Binding("2", "start_quest(2)", ""),
    ]
    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.quests = load_quests()
        if not self.quests:
            # Minimal sample quest
            sample_quest = Quest("Pilgrim of Stars", ["Observe night sky 3 times", "Write a cosmic poem"], completed=False)
            self.quests.append(sample_quest)
            save_quests(self.quests)

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*       Cosmic Quests      *",
            "****************************",
            ""
        ]
        for i, q in enumerate(self.quests, start=1):
            status = "[DONE]" if q.completed else "[ONGOING]"
            lines.append(f"{i}. {q.name} {status} - {q.tasks}")

        lines.append("\nPress number key to 'start/do' quest tasks. (b) to back.")
        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")

        yield Static("\n".join(lines), id="quests_text")

    def on_mount(self) -> None:
        qt = self.query_one("#quests_text", Static)
        qt.styles.background = self.app.cosmic_theme["background"]
        qt.styles.color = self.app.cosmic_theme["foreground"]
        qt.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_start_quest(self, number: str) -> None:
        idx = int(number) - 1
        if 0 <= idx < len(self.quests):
            q = self.quests[idx]
            # Mark as completed for demo
            q.completed = True
            save_quests(self.quests)
            beep()
            self.notification = f"You completed quest: {q.name}!"
            self.refresh()


# -------------- STEP 50: COSMIC CRAFTS SCREEN --------------
class CosmicCraftsScreen(Screen):
    """
    Rename or enhance artifacts, ownership & possession.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("1", "rename_artifact(1)", ""),
        Binding("2", "rename_artifact(2)", ""),
        Binding("3", "rename_artifact(3)", ""),
        Binding("4", "rename_artifact(4)", ""),
    ]
    notification: var[str] = var("")

    def __init__(self):
        super().__init__()
        self.artifacts = load_artifacts()

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*      Cosmic Crafts       *",
            "****************************",
            "",
            "Press number keys to rename artifact. (b) to go back."
        ]
        for i, art in enumerate(self.artifacts, start=1):
            status = "[COLLECTED]" if art.collected else "[UNCOLLECTED]"
            lines.append(f"{i}. {status} {art.name}")

        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")

        yield Static("\n".join(lines), id="crafts_text")

    def on_mount(self) -> None:
        ct = self.query_one("#crafts_text", Static)
        ct.styles.background = self.app.cosmic_theme["background"]
        ct.styles.color = self.app.cosmic_theme["foreground"]
        ct.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_rename_artifact(self, number: str) -> None:
        idx = int(number) - 1
        if 0 <= idx < len(self.artifacts):
            new_name = f"{self.artifacts[idx].name}-Enhanced"
            self.artifacts[idx].name = new_name
            save_artifacts(self.artifacts)
            beep()
            self.notification = f"Renamed to {new_name}"
            self.refresh()


# -------------- STEP 51: OFFLINE COMMUNITY (Export/Import) --------------
class ExportImportScreen(Screen):
    """
    Export or import entire data set to share offline.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
        Binding("e", "export_data", "Export"),
        Binding("i", "import_data", "Import"),
    ]
    notification: var[str] = var("")

    def compose(self) -> ComposeResult:
        lines = [
            "****************************",
            "*     Export / Import      *",
            "****************************",
            "",
            "Press (e) to export all data to export.json, (i) to import from it. (b) to back."
        ]
        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")
        yield Static("\n".join(lines), id="export_import_text")

    def on_mount(self) -> None:
        eit = self.query_one("#export_import_text", Static)
        eit.styles.background = self.app.cosmic_theme["background"]
        eit.styles.color = self.app.cosmic_theme["foreground"]
        eit.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()

    def action_export_data(self) -> None:
        export_all_data()
        beep()
        self.notification = "Exported to export.json!"
        self.refresh()

    def action_import_data(self) -> None:
        if os.path.exists("export.json"):
            import_all_data("export.json")
            beep()
            self.notification = "Imported from export.json!"
        else:
            self.notification = "export.json not found."
        self.refresh()

    def refresh(self):
        eit = self.query_one("#export_import_text", Static)
        lines = [
            "****************************",
            "*     Export / Import      *",
            "****************************",
            "",
            "Press (e) to export all data to export.json, (i) to import from it. (b) to back."
        ]
        if self.notification:
            lines.append(f"\n[NOTIFICATION] {self.notification}")
        eit.update("\n".join(lines))


# -------------- STEP 52: TEMPLE PILGRIMAGE SCREEN --------------
class TemplePilgrimageScreen(Screen):
    """
    An endgame or credits screen once big milestones are done.
    """

    BINDINGS = [
        Binding("b", "pop_screen", "Go back"),
    ]

    def compose(self) -> ComposeResult:
        lines = [
            "*******************************",
            "*   Temple Pilgrimage (End)   *",
            "*******************************",
            "",
            "You have reached the cosmic threshold!",
            "Thank you for exploring the Celestial Temple.",
            "Press (b) to return to Gate.",
        ]
        yield Static("\n".join(lines), id="pilgrimage_text")

    def on_mount(self) -> None:
        pt = self.query_one("#pilgrimage_text", Static)
        pt.styles.background = self.app.cosmic_theme["background"]
        pt.styles.color = self.app.cosmic_theme["foreground"]
        pt.styles.bold = True

    def action_pop_screen(self) -> None:
        self.app.pop_screen()