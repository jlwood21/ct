import asyncio
import os
import time

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.binding import Binding

from app.screens import TempleGateScreen, fade_transition
from app.settings_manager import load_settings, save_settings
from app.themes import THEMES


def startup_splash():
    """Print a retro ASCII splash, sleep briefly, then clear."""
    print(r"""
   _____                _             _   _____ _ 
  / ____|              | |           | | / ____(_)
 | |     _ __ ___  __ _| |_ ___  _ __| || |     _ 
 | |    | '__/ _ \/ _` | __/ _ \| '__| || |    | |
 | |____| | |  __/ (_| | || (_) | |  | || |____| |
  \_____|_|  \___|\__,_|\__\___/|_|  |_| \_____|_|

Booting CosmicTemple OS... Please stand by.
""")
    # Optional beep
    print("\a")  # Simple console bell
    time.sleep(1.5)  # Pause for effect

    # Clear screen (ANSI)
    print("\033c", end="")


class CosmicTempleApp(App):
    """A retro cosmic TUI app with extended TempleOS-style features."""

    BINDINGS = [
        Binding("enter", "goto_temple_gate", "Open Temple Gate"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Show the retro splash
        startup_splash()

        # Load user settings
        loaded = load_settings()
        self.current_theme_name = loaded.get("theme", "default")
        self.cosmic_theme = THEMES.get(self.current_theme_name, THEMES["default"])

    def compose(self) -> ComposeResult:
        # Banner after the splash
        banner_text = r"""
   ________  _________  ________  ___  ___          
  |\   ___ \|\___   ___\\   __  \|\  \|\  \         
  \ \  \_|\ \|___ \  \_\ \  \|\  \ \  \ \  \        
   \ \  \ \\ \   \ \  \ \ \   __  \ \  \ \  \       
    \ \  \_\\ \   \ \  \ \ \  \ \  \ \  \ \  \____  
     \ \_______\   \ \__\ \ \__\ \__\ \__\ \_______\
      \|_______|    \|__|  \|__|\|__|\|__|\|_______|

                 COSMIC TEMPLE

Press [ENTER] to open The Temple Gate.
        """
        banner = Static(banner_text, id="banner")
        yield banner

    def on_mount(self) -> None:
        banner = self.query_one("#banner", Static)
        banner.styles.background = self.cosmic_theme["background"]
        banner.styles.color = self.cosmic_theme["foreground"]
        banner.styles.bold = True

    async def action_goto_temple_gate(self) -> None:
        await fade_transition(self)
        self.push_screen(TempleGateScreen())

    def set_theme(self, theme_name: str) -> None:
        """Switch theme and save."""
        from app.settings_manager import load_settings, save_settings
        self.current_theme_name = theme_name
        self.cosmic_theme = THEMES.get(theme_name, THEMES["default"])
        settings = load_settings()
        settings["theme"] = theme_name
        save_settings(settings)


if __name__ == "__main__":
    CosmicTempleApp().run()