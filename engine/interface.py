# interface.py - Frontend interface for text adventure engine
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any, Callable, Set


class GameInterface(ABC):
    """
    Abstract base class for game interfaces.
    All frontend implementations must implement these methods.
    """
    
    def __init__(self):
        self.engine = None
        self.running = False
        self.display_needs_refresh = True
        self.special_commands = {
            "help": self._cmd_help,
            "quit": self._cmd_quit,
            "exit": self._cmd_quit,
            "q": self._cmd_quit,
            "undo": self._cmd_undo,
            "save": self._cmd_save,
            "load": self._cmd_load,
            "saves": self._cmd_list_saves,
            "list": self._cmd_list_saves,
            "delete": self._cmd_delete,
            "restart": self._cmd_restart
        }
    
    def initialize(self, engine) -> bool:
        """
        Initialize the interface.
        
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
        self._display_message("Thank you for playing!")
    
    @abstractmethod
    def _display_message(self, message: str) -> None:
        """
        Display a message to the user.
        
        Args:
            message: Message text to display
        """
        pass
    
    @abstractmethod
    def _display_scene(self, scene_text: str) -> None:
        """
        Display a scene to the user.
        
        Args:
            scene_text: Scene text to display
        """
        pass
    
    @abstractmethod
    def _display_choices(self, choices: List[str]) -> None:
        """
        Display choices to the user.
        
        Args:
            choices: List of choice texts
        """
        pass
    
    @abstractmethod
    def _get_user_input(self, prompt: str = "") -> str:
        """
        Get input from the user.
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            User input as a string
        """
        pass
    
    @abstractmethod
    def _confirm(self, message: str) -> bool:
        """
        Ask the user for confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if confirmed, False otherwise
        """
        pass
    
    @abstractmethod
    def _display_title(self, title: str) -> None:
        """
        Display a title.
        
        Args:
            title: Title to display
        """
        pass
    
    @abstractmethod
    def _clear_screen(self) -> None:
        """Clear the screen."""
        pass
    
    @abstractmethod
    def _display_saves(self, saves: List[Dict[str, Any]]) -> None:
        """
        Display a list of saves.
        
        Args:
            saves: List of save info dictionaries
        """
        pass
    
    def refresh_display(self) -> None:
        """Refresh the entire display with current game state."""
        if not self.engine:
            return
            
        scene_text = self.engine.get_current_scene_text()
        choices = self.engine.get_choice_texts()
        
        self._clear_screen()
        
        # Display current scene
        self._display_scene(scene_text)
        
        # Display choices
        if choices:
            self._display_choices(choices)
        else:
            self._display_message("THE END")
        
        # Mark display as refreshed
        self.display_needs_refresh = False
    
    def handle_special_command(self, command: str) -> bool:
        """
        Handle special commands like save, load, etc.
        
        Args:
            command: User command
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        parts = command.lower().split()
        base_cmd = parts[0] if parts else ""
        
        # Check if this is a known special command
        if base_cmd in self.special_commands:
            # Call the appropriate handler method
            handler = self.special_commands[base_cmd]
            handler(command)
            return True
            
        return False
    
    def process_command_result(self, command: str, result: str, refresh_display: bool = True) -> None:
        """
        Process and display the result of a command.
        
        Args:
            command: Original command
            result: Command result text
            refresh_display: Whether to refresh the full display
        """
        # Display command result
        self._display_message(result)
        
        # Refresh display if needed
        if refresh_display and self.display_needs_refresh:
            self.refresh_display()
    
    def _cmd_help(self, command: str) -> None:
        """Handle help command."""
        help_text = (
            "Available commands:\n"
            "- help: Show this help message\n"
            "- undo: Undo the last action\n"
            "- save [name]: Save the game\n"
            "- load [name]: Load a saved game\n"
            "- saves: List all saved games\n"
            "- delete [name]: Delete a saved game\n"
            "- restart: Restart the game\n"
            "- quit: Exit the game"
        )
        self._display_message(help_text)
    
    def _cmd_quit(self, command: str) -> None:
        """Handle quit command."""
        if self._confirm("Do you really want to quit?"):
            self.running = False
    
    def _cmd_undo(self, command: str) -> None:
        """Handle undo command."""
        result = self.engine.process_text_command("undo")
        self._display_message(result)
        self.display_needs_refresh = True
    
    def _cmd_save(self, command: str) -> None:
        """Handle save command."""
        parts = command.split()
        if len(parts) > 1:
            save_name = parts[1]
            result = self.engine.process_text_command(f"save {save_name}")
        else:
            result = self.engine.process_text_command("save")
        self._display_message(result)
    
    def _cmd_load(self, command: str) -> None:
        """Handle load command."""
        parts = command.split()
        if len(parts) > 1:
            save_name = parts[1]
            result = self.engine.process_text_command(f"load {save_name}")
            self._display_message(result)
            self.display_needs_refresh = True
        else:
            # Show available saves
            saves = self.engine.save_system.list_saves()
            self._display_saves(saves)
    
    def _cmd_list_saves(self, command: str) -> None:
        """Handle saves/list command."""
        saves = self.engine.save_system.list_saves()
        self._display_saves(saves)
    
    def _cmd_delete(self, command: str) -> None:
        """Handle delete command."""
        parts = command.split()
        if len(parts) > 1:
            save_name = parts[1]
            result = self.engine.process_text_command(f"delete {save_name}")
            self._display_message(result)
        else:
            self._display_message("Please specify a save name to delete.")
    
    def _cmd_restart(self, command: str) -> None:
        """Handle restart command."""
        if self._confirm("Do you really want to restart the game?"):
            # Reload current story
            story_id = self.engine.current_story_id
            self.engine.load_story(story_id)
            self.engine.initialize_game()
            self.display_needs_refresh = True
    
    def get_choice(self) -> int:
        """
        Get a choice from the user, handling special commands.
        
        Returns:
            int: Index of chosen choice (-1 for invalid/quit)
        """
        choices = self.engine.get_choice_texts()
        if not choices:
            return -1
        
        while True:
            user_input = self._get_user_input().strip()
            
            # Check for special commands
            if self.handle_special_command(user_input):
                # If game is no longer running (e.g., quit command)
                if not self.running:
                    return -1
                
                # If display needs refresh after command
                if self.display_needs_refresh:
                    self.refresh_display()
                continue
            
            # Try to parse as a choice number
            try:
                choice_num = int(user_input)
                if 1 <= choice_num <= len(choices):
                    return choice_num - 1
                else:
                    self._display_message(f"Please enter a number between 1 and {len(choices)}.")
            except ValueError:
                self._display_message("Please enter a number or command.")
    
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
        
        self._display_message(prompt)
        
        for i, item in enumerate(items, 1):
            self._display_message(f"{i}. {item}")
        
        while True:
            user_input = self._get_user_input("Enter your choice")
            
            # Check for quit/cancel
            if user_input.lower() in ["quit", "exit", "cancel", "q"]:
                return -1
            
            # Parse as number
            try:
                choice_num = int(user_input)
                if 1 <= choice_num <= len(items):
                    return choice_num - 1
                else:
                    self._display_message(f"Please enter a number between 1 and {len(items)}.")
            except ValueError:
                self._display_message("Please enter a number.")
    
    @abstractmethod
    def _wait_for_input(self, prompt: str = "Press enter to continue...") -> None:
        """
        Wait for the user to press enter to continue.
        
        Args:
            prompt: Message to show while waiting
        """
        pass
    
    def game_loop(self) -> None:
        """Run the main game loop."""
        if not self.engine:
            self._display_message("Error: No game engine initialized.")
            return
        
        # Display welcome message
        self._clear_screen()
        self._display_title(f"Welcome to {self.engine.title}")
        
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
            
            # Clear screen before showing result
            self._clear_screen()
            
            # Mark display as needing refresh
            self.display_needs_refresh = True
            
            # Handle the choice and get result
            result = self.engine.handle_choice(choice_index)
            
            # Show result and wait for user to continue
            if result and result != "You made your choice.":
                self._display_message(f"\n{result}\n")
                self._wait_for_input()
            
            # Now refresh display with the new scene
            self._clear_screen()
            self.refresh_display()
        
        # Clean up
        self.shutdown()