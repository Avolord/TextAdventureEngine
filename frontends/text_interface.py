# text_interface.py - Text-based frontend implementation
import os
import sys
from typing import List, Optional, Tuple, Dict, Any

from engine.interface import GameInterface


class TextInterface(GameInterface):
    """
    Text-based interface for the text adventure engine.
    Uses console input/output for interaction.
    """
    
    def __init__(self):
        self.width = 80  # Default terminal width
        self.engine = None
        self.running = False
        
        # Try to get actual terminal size
        try:
            terminal_size = os.get_terminal_size()
            self.width = terminal_size.columns
        except (AttributeError, OSError):
            pass  # Stick with default width
    
    def initialize(self, engine) -> bool:
        """
        Initialize the text interface.
        
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
        print("\nThank you for playing!\n")
    
    def display_message(self, message: str) -> None:
        """
        Display a message to the user.
        
        Args:
            message: Message text to display
        """
        print(message)
    
    def display_scene(self, scene_text: str) -> None:
        """
        Display a scene to the user.
        
        Args:
            scene_text: Scene text to display
        """
        print("\n" + scene_text + "\n")
    
    def display_choices(self, choices: List[str]) -> None:
        """
        Display choices to the user.
        
        Args:
            choices: List of choice texts
        """
        if not choices:
            print("No choices available.")
            return
        
        print("Available choices:")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        print("\nSpecial commands: save, load, saves, restart, help, quit")
    
    def get_user_input(self, prompt: str = "") -> str:
        """
        Get input from the user.
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            User input as a string
        """
        if prompt:
            return input(f"{prompt} ")
        return input("> ")
    
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
            user_input = self.get_user_input("\nWhat will you do?").strip()
            
            # Check for special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                return -1
            
            # Check for other special commands
            if user_input.lower() in ["save", "load", "saves", "list", "help", "restart"] or \
               user_input.lower().startswith(("save ", "load ")):
                result = self.engine.process_text_command(user_input)
                print("\n" + result + "\n")
                self.display_choices(choices)
                continue
            
            # Try to parse as a choice number
            try:
                choice_num = int(user_input)
                if 1 <= choice_num <= len(choices):
                    return choice_num - 1
                else:
                    print(f"Please enter a number between 1 and {len(choices)}.")
            except ValueError:
                print("Please enter a number or command.")
    
    def select_from_list(self, items: List[str], prompt: str) -> int:
        """
        Let the user select an item from a list.
        
        Args:
            items: List of items
            prompt: Prompt to display
            
        Returns:
            Index of selected item (-1 for invalid/cancel)
        """
        if not items:
            return -1
        
        print(prompt)
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")
        
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
                    print(f"Please enter a number between 1 and {len(items)}.")
            except ValueError:
                print("Please enter a number.")
    
    def confirm(self, message: str) -> bool:
        """
        Ask the user for confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if confirmed, False otherwise
        """
        print(message)
        while True:
            response = self.get_user_input("(y/n)").lower()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                print("Please enter 'y' or 'n'.")
    
    def display_title(self, title: str) -> None:
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
    
    def clear_screen(self) -> None:
        """Clear the screen."""
        # Try platform-specific clear commands
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")
    
    def game_loop(self, engine) -> None:
        """
        Run the main game loop.
        
        Args:
            engine: Game engine instance
        """
        self.engine = engine
        self.running = True
        
        # Display welcome message
        self.display_title(f"Welcome to {engine.title}")
        
        while self.running:
            # Display current scene
            scene_text = engine.get_current_scene_text()
            self.display_scene(scene_text)
            
            # Get available choices
            choices = engine.get_choice_texts()
            
            # If no choices, assume end of game
            if not choices:
                print("\nTHE END")
                
                self.running = False
                break
            
            # Get player choice
            choice_index = self.get_choice(choices)
            
            # Check for quit
            if choice_index < 0:
                # Offer to save before quitting
                if not self.confirm("Do you really want to quit?"):
                    continue
                
                self.running = False
                break
            
            self.clear_screen()
            
            # Process choice
            result = engine.handle_choice(choice_index)
            self.display_message(result)
        
        # Clean up
        self.shutdown()


def create_text_interface() -> TextInterface:
    """
    Create a new text interface.
    
    Returns:
        TextInterface instance
    """
    return TextInterface()