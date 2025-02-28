# interface.py - Frontend interface for text adventure engine
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any, Callable


class GameInterface(ABC):
    """
    Abstract base class for game interfaces.
    All frontend implementations must implement these methods.
    """
    
    @abstractmethod
    def initialize(self, engine) -> bool:
        """
        Initialize the interface.
        
        Args:
            engine: Game engine instance
            
        Returns:
            bool: True if initialization was successful
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Clean up resources when shutting down the interface."""
        pass
    
    @abstractmethod
    def display_message(self, message: str) -> None:
        """
        Display a message to the user.
        
        Args:
            message: Message text to display
        """
        pass
    
    @abstractmethod
    def display_scene(self, scene_text: str) -> None:
        """
        Display a scene to the user.
        
        Args:
            scene_text: Scene text to display
        """
        pass
    
    @abstractmethod
    def display_choices(self, choices: List[str]) -> None:
        """
        Display choices to the user.
        
        Args:
            choices: List of choice texts
        """
        pass
    
    @abstractmethod
    def get_user_input(self, prompt: str = "") -> str:
        """
        Get input from the user.
        
        Args:
            prompt: Optional prompt to display
            
        Returns:
            User input as a string
        """
        pass
    
    @abstractmethod
    def get_choice(self, choices: List[str]) -> int:
        """
        Get a choice from the user.
        
        Args:
            choices: List of choice texts
            
        Returns:
            Index of chosen choice
        """
        pass
    
    @abstractmethod
    def select_from_list(self, items: List[str], prompt: str) -> int:
        """
        Let the user select an item from a list.
        
        Args:
            items: List of items
            prompt: Prompt to display
            
        Returns:
            Index of selected item
        """
        pass
    
    @abstractmethod
    def confirm(self, message: str) -> bool:
        """
        Ask the user for confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if confirmed, False otherwise
        """
        pass
    
    @abstractmethod
    def display_title(self, title: str) -> None:
        """
        Display a title.
        
        Args:
            title: Title to display
        """
        pass
    
    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the screen."""
        pass
    
    @abstractmethod
    def game_loop(self, engine) -> None:
        """
        Run the main game loop.
        
        Args:
            engine: Game engine instance
        """
        pass


class InterfaceManager:
    """
    Manages the current interface and provides access to it.
    """
    def __init__(self):
        self.current_interface = None
    
    def set_interface(self, interface: GameInterface) -> None:
        """
        Set the current interface.
        
        Args:
            interface: Interface to set as current
        """
        self.current_interface = interface
    
    def get_interface(self) -> Optional[GameInterface]:
        """
        Get the current interface.
        
        Returns:
            Current interface or None if not set
        """
        return self.current_interface
    
    def is_initialized(self) -> bool:
        """
        Check if an interface is set.
        
        Returns:
            True if an interface is set, False otherwise
        """
        return self.current_interface is not None