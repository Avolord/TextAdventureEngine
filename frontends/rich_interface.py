# rich_interface.py - Rich-based enhanced frontend implementation
import os
import sys
import time
from typing import List, Optional, Tuple, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.style import Style
from rich.theme import Theme
from rich.prompt import Prompt, Confirm
from rich.spinner import Spinner

from engine.interface import GameInterface


class RichInterface(GameInterface):
    """
    Enhanced text-based interface for the text adventure engine.
    Uses the Rich library for prettier console output.
    """
    
    def __init__(self):
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
        self.engine = None
        self.running = False
        self.current_scene_id = None  # Track current scene to avoid duplication
        
        # Get terminal size
        self.width = self.console.width
        self.height = self.console.height
    
    def initialize(self, engine) -> bool:
        """
        Initialize the rich interface.
        
        Args:
            engine: Game engine instance
            
        Returns:
            bool: True if initialization was successful
        """
        self.engine = engine
        self.running = True
        return True
    
    def shutdown(self) -> None:
        """Clean up resources when shutting down the interface."""
        self.running = False
        self.display_message("[success]Thank you for playing![/success]")
    
    def display_message(self, message: str) -> None:
        """
        Display a message to the user.
        
        Args:
            message: Message text to display (can include Rich markup)
        """
        if message:  # Only display if there's a message
            self.console.print(message)
    
    def display_scene(self, scene_text: str) -> None:
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
    
    def display_choices(self, choices: List[str]) -> None:
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
        commands_text = Text("Special commands: ", style="command")
        commands_text.append("save", style="command")
        commands_text.append(", ")
        commands_text.append("load", style="command")
        commands_text.append(", ")
        commands_text.append("saves", style="command")
        commands_text.append(", ")
        commands_text.append("restart", style="command")
        commands_text.append(", ")
        commands_text.append("help", style="command")
        commands_text.append(", ")
        commands_text.append("quit", style="command")
        
        self.console.print(commands_text)
    
    def get_user_input(self, prompt: str = "") -> str:
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
    
    def get_choice(self, choices: List[str]) -> int:
        """
        Get a choice from the user.
        
        Args:
            choices: List of choice texts
            
        Returns:
            Index of chosen choice (-1 for invalid/quit)
        """
        if not choices:
            return -1
        
        self.display_choices(choices)
        
        while True:
            user_input = self.get_user_input().strip()
            
            # Check for special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                return -1
            
            # Check for other special commands
            if user_input.lower() in ["save", "load", "saves", "list", "help", "restart"] or \
               user_input.lower().startswith(("save ", "load ")):
                result = self.engine.process_text_command(user_input)
                self.console.print(Panel(result, border_style="info"))
                self.display_choices(choices)
                continue
            
            # Try to parse as a choice number
            try:
                choice_num = int(user_input)
                if 1 <= choice_num <= len(choices):
                    return choice_num - 1
                else:
                    self.console.print(f"[warning]Please enter a number between 1 and {len(choices)}.[/warning]")
            except ValueError:
                self.console.print("[warning]Please enter a number or command.[/warning]")
    
    def select_from_list(self, items: List[str], prompt: str) -> int:
        """
        Let the user select an item from a list using a Rich Table.
        
        Args:
            items: List of items
            prompt: Prompt to display
            
        Returns:
            Index of selected item (-1 for invalid/cancel)
        """
        if not items:
            return -1
        
        # Display options in a table
        table = Table(show_header=False, box=None, padding=(0, 1, 0, 1))
        table.add_column("Number", style="choice", justify="right")
        table.add_column("Item", style="choice")
        
        for i, item in enumerate(items, 1):
            table.add_row(f"{i}.", item)
        
        # Show prompt and table
        self.console.print(Panel(prompt, border_style="info"))
        self.console.print(table)
        
        while True:
            try:
                user_input = self.get_user_input("Enter your choice")
                
                # Check for quit/cancel
                if user_input.lower() in ["quit", "exit", "cancel", "q"]:
                    return -1
                
                # Parse as number
                choice_num = int(user_input)
                if 1 <= choice_num <= len(items):
                    return choice_num - 1
                else:
                    self.console.print(f"[warning]Please enter a number between 1 and {len(items)}.[/warning]")
            except ValueError:
                self.console.print("[warning]Please enter a number.[/warning]")
    
    def confirm(self, message: str) -> bool:
        """
        Ask the user for confirmation using Rich Confirm.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if confirmed, False otherwise
        """
        return Confirm.ask(message)
    
    def display_title(self, title: str) -> None:
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
    
    def clear_screen(self) -> None:
        """Clear the screen."""
        self.console.clear()
    
    def show_transition_effect(self) -> None:
        """Show a brief transition effect."""
        with self.console.status("", spinner="dots"):
            time.sleep(0.5)  # Brief pause for effect
    
    def game_loop(self, engine) -> None:
        """
        Run the main game loop with Rich enhancements.
        
        Args:
            engine: Game engine instance
        """
        self.engine = engine
        self.running = True
        
        # Display welcome message
        self.clear_screen()
        self.display_title(f"Welcome to {engine.title}")
        
        # Brief pause for effect
        self.show_transition_effect()
        self.clear_screen()
        
        # Initialize scene tracking
        current_scene = engine.get_current_scene()
        if current_scene:
            self.current_scene_id = current_scene.scene_id
            
            # Display initial scene
            scene_text = engine.get_current_scene_text()
            self.display_scene(scene_text)
        
        while self.running:
            # Get available choices
            choices = engine.get_choice_texts()
            
            # If no choices, assume end of game
            if not choices:
                self.console.print(Panel("[success]THE END[/success]", border_style="success"))
                self.running = False
                break
            
            # Get player choice
            choice_index = self.get_choice(choices)
            
            # Check for quit
            if choice_index < 0:
                # Offer to save before quitting
                if not self.confirm("[warning]Do you really want to quit?[/warning]"):
                    continue
                
                self.running = False
                break
            
            # Get current scene ID before handling choice
            old_scene_id = self.current_scene_id
            
            # Show brief transition
            self.show_transition_effect()
            
            # Clear screen and process choice
            self.clear_screen()
            result = engine.handle_choice(choice_index)
            
            # Get new scene ID and update tracking
            current_scene = engine.get_current_scene()
            if current_scene:
                new_scene_id = current_scene.scene_id
                self.current_scene_id = new_scene_id
                
                # Only display scene text if we've moved to a new scene
                if new_scene_id != old_scene_id:
                    scene_text = engine.get_current_scene_text()
                    self.display_scene(scene_text)
                else:
                    # Display result from choice if not a scene transition
                    self.display_message(result)
            else:
                # Just display the result
                self.display_message(result)
        
        # Clean up
        self.shutdown()


def create_rich_interface() -> RichInterface:
    """
    Create a new Rich-enhanced interface.
    
    Returns:
        RichInterface instance
    """
    return RichInterface()