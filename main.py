from textual.app import App, ComposeResult
from textual.widgets import Static

class CosmicTempleApp(App):
    """A retro cosmic TUI app inspired by TempleOS aesthetics."""

    def compose(self) -> ComposeResult:
        # Create a Static widget for the ASCII banner (raw string to avoid escape issues)
        banner_text = r"""
  _______  _____  _____  
 |__   __||  __ \|  __ \ 
    | |   | |__) | |__) |
    | |   |  ___/|  _  / 
    | |   | |    | | \ \ 
    |_|   |_|    |_|  \_\
            
Welcome to the Cosmic Temple! 
Press CTRL+C (or CTRL+\ on some systems) to exit at any time.
        """

        banner = Static(banner_text, id="banner")
        # We'll yield (return) the banner in the compose result
        yield banner

    def on_mount(self) -> None:
        """Called after widgets are mounted; set the banner's style here."""
        banner = self.query_one("#banner", Static)
        # Set textual styles programmatically
        banner.styles.background = "black"  # Background color
        banner.styles.color = "white"       # Text color
        banner.styles.bold = True           # Bold text

if __name__ == "__main__":
    CosmicTempleApp().run()
