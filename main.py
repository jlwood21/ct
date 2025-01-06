from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.binding import Binding

from app.screens import TempleGateScreen
from app.settings_manager import load_settings
from app.themes import THEMES


class CosmicTempleApp(App):
    """A retro cosmic TUI app inspired by TempleOS aesthetics, featuring multiple screens and theming."""

    # Press "enter" on the banner to go to the Temple Gate.
    BINDINGS = [
        Binding("enter", "goto_temple_gate", "Open Temple Gate"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load user settings (if any)
        loaded = load_settings()
        theme_name = loaded.get("theme", "default")
        self.theme = THEMES.get(theme_name, THEMES["default"])

    def compose(self) -> ComposeResult:
        # Updated ASCII banner (raw string to avoid escape sequences)
        banner_text = r"""
   ________  _________  ________  ___  ___          
  |\   ___ \|\___   ___\\   __  \|\  \|\  \         
  \ \  \_|\ \|___ \  \_\ \  \|\  \ \  \ \  \        
   \ \  \ \\ \   \ \  \ \ \   __  \ \  \ \  \       
    \ \  \_\\ \   \ \  \ \ \  \ \  \ \  \ \  \____  
     \ \_______\   \ \__\ \ \__\ \__\ \__\ \_______\
      \|_______|    \|__|  \|__|\|__|\|__|\|_______|

                 COSMIC TEMPLE

Welcome to the Cosmic Temple! 
Press CTRL+C (or CTRL+\) to exit at any time.
Press [ENTER] to open The Temple Gate.
        """

        banner = Static(banner_text, id="banner")
        yield banner

    def on_mount(self) -> None:
        """Style the banner according to the current theme."""
        banner = self.query_one("#banner", Static)
        banner.styles.background = self.theme["background"]
        banner.styles.color = self.theme["foreground"]
        banner.styles.bold = True

    def action_goto_temple_gate(self) -> None:
        """Push the Temple Gate screen."""
        self.push_screen(TempleGateScreen())

    def set_theme(self, theme_name: str):
        """Switch theme and save to settings."""
        from app.settings_manager import load_settings, save_settings
        self.theme = THEMES.get(theme_name, THEMES["default"])
        settings = load_settings()
        settings["theme"] = theme_name
        save_settings(settings)


if __name__ == "__main__":
    CosmicTempleApp().run()
