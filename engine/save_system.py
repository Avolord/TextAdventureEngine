# save_system.py - Save, load and undo functionality
import os
import json
import copy
from typing import Tuple, List, Dict, Any, Optional

from .game_state import GameState
from .character import Character, DynamicStats


class SaveSystem:
    """
    Manages game state saving, loading, and history for undo functionality.
    Implements saving/loading to files and an in-memory undo system.
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.state_history = []  # Stack of previous states for undo
        self.history_size = 50  # Maximum number of states to keep in history
        self.saves_directory = None
        
        # Create saves directory if not already set
        self._initialize_saves_directory()
    
    def _initialize_saves_directory(self):
        """Set up the saves directory."""
        if self.engine.stories_directory:
            # Use 'saves' directory at the same level as 'stories'
            base_dir = os.path.dirname(self.engine.stories_directory)
            self.saves_directory = os.path.join(base_dir, "saves")
            os.makedirs(self.saves_directory, exist_ok=True)
    
    def push_state(self):
        """Save the current state to the history stack for undo functionality."""
        if not self.engine.game_state_manager.state:
            return False
            
        if len(self.state_history) >= self.history_size:
            # Remove oldest state if we've hit the limit
            self.state_history.pop(0)
        
        # Create a copy of the current state
        state_copy = self._serialize_state()
        
        # Save story ID along with state
        state_data = {
            'story_id': self.engine.current_story_id,
            'state': state_copy
        }
        
        # Push to history
        self.state_history.append(state_data)
        return True
    
    def undo(self) -> Tuple[bool, str]:
        """
        Restore the previous state from history.
        
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        if not self.state_history:
            return False, "Nothing to undo."
        
        # Pop the most recent state
        state_data = self.state_history.pop()
        story_id = state_data['story_id']
        state_dict = state_data['state']
        
        # Restore the previous state
        return self._restore_state(story_id, state_dict)
    
    def _serialize_state(self) -> Dict:
        """
        Create a serializable representation of the current game state.
        
        Returns:
            Dict: Serialized state
        """
        state = self.engine.game_state_manager.state
        
        # Use the to_dict method we'll add to GameState
        return state.to_dict()
    
    def _restore_state(self, story_id: str, state_dict: Dict) -> Tuple[bool, str]:
        """
        Restore a saved game state.
        
        Args:
            story_id: ID of the story
            state_dict: Serialized state data
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        # Load the story if different from current
        if story_id != self.engine.current_story_id:
            if not self.engine.load_story(story_id):
                return False, f"Failed to load story: {story_id}"
        
        try:
            # Create a new GameState from the dictionary
            state = GameState.from_dict(state_dict)
            
            # Set it as the current state
            self.engine.game_state_manager.state = state
            
            # Clear scene cache to force recalculation with new state
            self.engine._scene_cache = {}
            
            return True, "Previous state restored."
        except Exception as e:
            return False, f"Error restoring state: {e}"
    
    def save_game(self, save_name: str) -> Tuple[bool, str]:
        """
        Save the current game to a file.
        
        Args:
            save_name: Name for the save
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        if not self.saves_directory:
            self._initialize_saves_directory()
            if not self.saves_directory:
                return False, "Save directory not set."
        
        if not self.engine.game_state_manager.state:
            return False, "No active game to save."
        
        try:
            # Create save data
            save_data = {
                'story_id': self.engine.current_story_id,
                'title': self.engine.title,
                'state': self._serialize_state(),
                'timestamp': self._get_timestamp()
            }
            
            # Create save file path
            filepath = os.path.join(self.saves_directory, f"{save_name}.save")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(save_data, file, indent=2)
            
            return True, f"Game saved as '{save_name}'."
        except Exception as e:
            return False, f"Error saving game: {e}"
    
    def _get_timestamp(self) -> str:
        """Get a timestamp for the save file."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def load_game(self, save_name: str) -> Tuple[bool, str]:
        """
        Load a saved game from a file.
        
        Args:
            save_name: Name of the save to load
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        if not self.saves_directory:
            self._initialize_saves_directory()
            if not self.saves_directory:
                return False, "Save directory not set."
        
        # Handle file extensions
        if not save_name.endswith('.save'):
            filepath = os.path.join(self.saves_directory, f"{save_name}.save")
        else:
            filepath = os.path.join(self.saves_directory, save_name)
        
        if not os.path.exists(filepath):
            return False, f"Save file '{save_name}' not found."
        
        try:
            # Read save file
            with open(filepath, 'r', encoding='utf-8') as file:
                save_data = json.load(file)
            
            story_id = save_data.get('story_id')
            state_dict = save_data.get('state')
            
            if not story_id or not state_dict:
                return False, "Invalid save data."
            
            # Restore the state
            return self._restore_state(story_id, state_dict)
        except Exception as e:
            return False, f"Error loading game: {e}"
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """
        List all available save files.
        
        Returns:
            List of save info dictionaries with name, timestamp, title, etc.
        """
        if not self.saves_directory or not os.path.exists(self.saves_directory):
            return []
        
        saves = []
        for filename in os.listdir(self.saves_directory):
            if filename.endswith('.save'):
                filepath = os.path.join(self.saves_directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        save_data = json.load(file)
                    
                    # Extract save info
                    save_name = os.path.splitext(filename)[0]
                    timestamp = save_data.get('timestamp', 'Unknown')
                    title = save_data.get('title', 'Unknown')
                    story_id = save_data.get('story_id', 'Unknown')
                    
                    saves.append({
                        'name': save_name,
                        'timestamp': timestamp,
                        'title': title,
                        'story_id': story_id
                    })
                except Exception:
                    # Skip corrupted save files
                    continue
        
        # Sort by timestamp, newest first
        saves.sort(key=lambda x: x['timestamp'], reverse=True)
        return saves
    
    def delete_save(self, save_name: str) -> Tuple[bool, str]:
        """
        Delete a save file.
        
        Args:
            save_name: Name of the save to delete
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        if not self.saves_directory:
            return False, "Save directory not set."
        
        if not save_name.endswith('.save'):
            filepath = os.path.join(self.saves_directory, f"{save_name}.save")
        else:
            filepath = os.path.join(self.saves_directory, save_name)
        
        if not os.path.exists(filepath):
            return False, f"Save file '{save_name}' not found."
        
        try:
            os.remove(filepath)
            return True, f"Save '{save_name}' deleted."
        except Exception as e:
            return False, f"Error deleting save: {e}"