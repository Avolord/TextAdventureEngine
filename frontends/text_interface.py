# text_interface.py - Text-based frontend implementation
import os
import sys
from typing import List, Dict, Any

from engine.interface import GameInterface


class TextInterface(GameInterface):
    """
    Text-based interface for the text adventure engine.
    Uses console input/output for interaction.
    """
    
    def __init__(self):
        super().__init__()
        self.width = 80  # Default terminal width
        
        # Try to get actual terminal size
        try:
            terminal_size = os.get_terminal_size()
            self.width = terminal_size.columns
        except (AttributeError, OSError):
            pass  # Stick with default width
    
    def _display_message(self, message: str) -> None:
        """
        Display a message to the user.
        
        Args:
            message: Message text to display
        """
        if message:  # Only display if there's a message
            print(message)
    
    def _display_scene(self, scene_text: str) -> None:
        """
        Display a scene to the user.
        
        Args:
            scene_text: Scene text to display
        """
        print("\n" + scene_text + "\n")
    
    def _display_choices(self, choices: List[str]) -> None:
        """
        Display choices to the user.
        
        Args:
            choices: List of choice texts
        """
        if not choices:
            print("No choices available.")
            return
        
        print("\nAvailable choices:")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        print("\nSpecial commands: help, undo, save, load, saves, delete, restart, quit")
    
    def _get_user_input(self, prompt: str = "") -> str:
        """
        Get input from the user.
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            User input as a string
        """
        if prompt:
            return input(f"{prompt} ")
        return input("\n> ")
    
    def _confirm(self, message: str) -> bool:
        """
        Ask the user for confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if confirmed, False otherwise
        """
        print(message)
        while True:
            response = self._get_user_input("(y/n)").lower()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                print("Please enter 'y' or 'n'.")
    
    def _display_title(self, title: str) -> None:
        """
        Display a title.
        
        Args:
            title: Title to display
        """
        title_length = len(title)
        padding = max(10, (self.width - title_length) // 2)
        border = "=" * self.width
        
        print("\n" + border)
        print(" " * padding + title)
        print(border + "\n")
    
    def _clear_screen(self) -> None:
        """Clear the screen."""
        # Try platform-specific clear commands
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")
    
    def _display_saves(self, saves: List[Dict[str, Any]]) -> None:
        """
        Display a list of saves.
        
        Args:
            saves: List of save info dictionaries
        """
        if not saves:
            print("No saved games found.")
            return
        
        print("\nAvailable saves:")
        for i, save in enumerate(saves, 1):
            print(f"{i}. {save['name']} - {save['title']} ({save['timestamp']})")
        
        print("\nUse 'load [name]' to load a specific save.")
    
    def _wait_for_input(self, prompt: str = "Press enter to continue...") -> None:
        """
        Wait for the user to press enter to continue.
        
        Args:
            prompt: Message to show while waiting
        """
        input(f"\n{prompt} ")


def create_text_interface() -> TextInterface:
    """
    Create a new text interface.
    
    Returns:
        TextInterface instance
    """
    return TextInterface()