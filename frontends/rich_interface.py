# rich_interface.py - Rich-based enhanced frontend implementation
import time
from typing import List, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.theme import Theme
from rich.prompt import Prompt, Confirm

from engine.interface import GameInterface


class RichInterface(GameInterface):
    """
    Enhanced text-based interface for the text adventure engine.
    Uses the Rich library for prettier console output.
    """
    
    def __init__(self):
        super().__init__()
        
        # Create theme for consistent styling
        custom_theme = Theme({
            "scene": "bold cyan",
            "title": "bold yellow",
            "choice": "green",
            "command": "bold blue",
            "warning": "bold red",
            "success": "bold green",
            "info": "italic",
            "stats": "yellow",
        })
        
        self.console = Console(theme=custom_theme, highlight=False)
        
        # Get terminal size
        self.width = self.console.width
        self.height = self.console.height
    
    def _display_message(self, message: str) -> None:
        """
        Display a message to the user.
        
        Args:
            message: Message text to display (can include Rich markup)
        """
        if message:  # Only display if there's a message
            self.console.print(message)
    
    def _display_scene(self, scene_text: str) -> None:
        """
        Display a scene to the user using Rich formatting.
        
        Args:
            scene_text: Scene text to display
        """
        # Process scene text for enhanced display
        # Check for lines that could be stats or special sections
        lines = scene_text.split('\n')
        formatted_lines = []
        
        in_stats_section = False
        stats_lines = []
        
        for line in lines:
            # Check if this is a stats line
            if line.strip().startswith('-') and ':' in line:
                if not in_stats_section:
                    in_stats_section = True
                stats_lines.append(line)
            elif in_stats_section and line.strip():
                # Still part of stats section
                stats_lines.append(line)
            elif in_stats_section:
                # End of stats section
                in_stats_section = False
                formatted_lines.append(self._format_stats_section(stats_lines))
                stats_lines = []
                if line.strip():
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        # Handle stats at the end of the text
        if in_stats_section and stats_lines:
            formatted_lines.append(self._format_stats_section(stats_lines))
        
        # Combine and wrap in a Panel
        formatted_text = '\n'.join(formatted_lines)
        scene_panel = Panel(
            Markdown(formatted_text),
            title="Scene",
            border_style="scene",
            expand=False,
            width=min(100, self.width - 4)
        )
        
        self.console.print(scene_panel)
    
    def _format_stats_section(self, stats_lines: List[str]) -> str:
        """Format a section of stats with Rich formatting."""
        formatted_stats = "[stats]"
        for line in stats_lines:
            formatted_stats += line + "\n"
        formatted_stats += "[/stats]"
        return formatted_stats
    
    def _display_choices(self, choices: List[str]) -> None:
        """
        Display choices to the user using a Rich Table.
        
        Args:
            choices: List of choice texts
        """
        if not choices:
            self.console.print("[warning]No choices available.[/warning]")
            return
        
        # Create a table for choices
        table = Table(title="Your Options", show_header=False, box=None, padding=(0, 1, 0, 1))
        table.add_column("Number", style="choice", justify="right")
        table.add_column("Choice", style="choice")
        
        for i, choice in enumerate(choices, 1):
            table.add_row(f"{i}.", choice)
        
        self.console.print(table)
        
        # Add command help
        commands_text = Text("\nSpecial commands: ", style="command")
        commands = ["help", "undo", "save", "load", "saves", "delete", "restart", "quit"]
        
        for i, cmd in enumerate(commands):
            commands_text.append(cmd, style="command")
            if i < len(commands) - 1:
                commands_text.append(", ")
        
        self.console.print(commands_text)
    
    def _get_user_input(self, prompt: str = "") -> str:
        """
        Get input from the user using Rich Prompt.
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            User input as a string
        """
        if not prompt:
            prompt = "What will you do?"
            
        return Prompt.ask(prompt)
    
    def _confirm(self, message: str) -> bool:
        """
        Ask the user for confirmation using Rich Confirm.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if confirmed, False otherwise
        """
        return Confirm.ask(message)
    
    def _display_title(self, title: str) -> None:
        """
        Display a title using Rich styling.
        
        Args:
            title: Title to display
        """
        title_panel = Panel(
            Text(title, style="title", justify="center"),
            border_style="title",
            width=min(80, self.width - 4),
            padding=(1, 10)
        )
        
        self.console.print(title_panel)
    
    def _clear_screen(self) -> None:
        """Clear the screen."""
        self.console.clear()
    
    def _display_saves(self, saves: List[Dict[str, Any]]) -> None:
        """
        Display a list of saves using a Rich Table.
        
        Args:
            saves: List of save info dictionaries
        """
        if not saves:
            self.console.print("[warning]No saved games found.[/warning]")
            return
        
        # Create a table for saves
        table = Table(title="Saved Games", box=True)
        table.add_column("Name", style="info")
        table.add_column("Story", style="info")
        table.add_column("Timestamp", style="info")
        
        for save in saves:
            table.add_row(
                save['name'],
                save['title'],
                save['timestamp']
            )
        
        self.console.print(table)
        self.console.print("\nUse [command]load [name][/command] to load a specific save.")
    
    def show_transition_effect(self) -> None:
        """Show a brief transition effect."""
        with self.console.status("", spinner="dots"):
            time.sleep(0.5)  # Brief pause for effect
    
    # Override process_command_result to add styling
    def process_command_result(self, command: str, result: str, refresh_display: bool = True) -> None:
        """
        Process and display the result of a command with styling.
        
        Args:
            command: Original command
            result: Command result text
            refresh_display: Whether to refresh the full display
        """
        # Display command result with appropriate styling
        cmd_base = command.split()[0].lower() if command else ""
        
        if cmd_base == "save":
            self.console.print(Panel(result, border_style="success"))
        elif cmd_base in ["load", "undo"]:
            self.console.print(Panel(result, border_style="info"))
        elif cmd_base == "delete":
            self.console.print(Panel(result, border_style="warning"))
        else:
            self.console.print(Panel(result, border_style="info"))
        
        # Refresh display if needed
        if refresh_display and self.display_needs_refresh:
            self.refresh_display()
    
    def _wait_for_input(self, prompt: str = "Press enter to continue...") -> None:
        """
        Wait for the user to press enter to continue with Rich styling.
        
        Args:
            prompt: Message to show while waiting
        """
        self.console.print(f"\n[command]{prompt}[/command]", end="")
        input(" ")
    
    # Override game_loop to add transition effects
    def game_loop(self) -> None:
        """Run the main game loop with Rich enhancements."""
        if not self.engine:
            self._display_message("[warning]Error: No game engine initialized.[/warning]")
            return
        
        # Display welcome message
        self._clear_screen()
        self._display_title(f"Welcome to {self.engine.title}")
        
        # Brief pause for effect
        self.show_transition_effect()
        
        # Display initial scene
        self.refresh_display()
        
        while self.running:
            # Get player choice (handling special commands)
            choice_index = self.get_choice()
            
            # Check for quit or invalid choice
            if choice_index < 0:
                if not self.running:  # Was quit command
                    break
                continue  # Invalid choice or handled command
            
            # Show brief transition effect
            self.show_transition_effect()
            
            # Clear screen before showing result
            self._clear_screen()
            
            # Mark display as needing refresh
            self.display_needs_refresh = True
            
            # Handle the choice and get result
            result = self.engine.handle_choice(choice_index)
            
            # Show result and wait for user to continue
            if result and result != "You made your choice.":
                # Display result in a styled panel
                self.console.print(Panel(
                    result,
                    title="Result",
                    border_style="info"
                ))
                self._wait_for_input()
            
            # Now refresh display with the new scene
            self._clear_screen()
            self.refresh_display()
        
        # Clean up
        self.shutdown()


def create_rich_interface() -> RichInterface:
    """
    Create a new Rich-enhanced interface.
    
    Returns:
        RichInterface instance
    """
    return RichInterface()