import os
import json
from typing import Dict, Optional, Any, List

from .character import Character, DynamicStats


class CharacterManager:
    """
    Manages character loading, saving, and persistence across stories.
    Works with the unified stats system.
    
    Templates are read-only and characters are only loaded from story definitions.
    Multiple characters can use the same template.
    """
    def __init__(self):
        self.characters = {}  # Dictionary of loaded character instances by name
        self.player_character = None  # Reference to the player character
        self.templates_directory = None  # Directory for character templates (read-only)
    
    def set_templates_directory(self, templates_dir: str):
        """
        Set the directory for character templates.
        
        Args:
            templates_dir: Directory for character templates (starting state)
        """
        self.templates_directory = templates_dir
        
        # Create directory if it doesn't exist
        os.makedirs(templates_dir, exist_ok=True)
    
    def get_template_filepath(self, name: str) -> str:
        """
        Get the filepath for a character template.
        
        Args:
            name: Character name or template filename
            
        Returns:
            Path to the character template file
        """
        if not self.templates_directory:
            raise ValueError("Templates directory not set")
        
        # If name already includes .tchar extension, use it directly
        if name.endswith('.tchar'):
            return os.path.join(self.templates_directory, name)
        
        # Otherwise, sanitize name for filename
        safe_name = self._sanitize_name(name)
        return os.path.join(self.templates_directory, f"{safe_name}.tchar")
    
    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize a name for use in a filename.
        
        Args:
            name: Character name
            
        Returns:
            Sanitized name
        """
        safe_name = ''.join(c for c in name if c.isalnum() or c in ' _-').strip()
        safe_name = safe_name.replace(' ', '_').lower()
        return safe_name
    
    def get_character(self, name: str) -> Optional[Character]:
        """
        Get a character by name.
        
        Args:
            name: Character name
            
        Returns:
            Character object or None if not found
        """
        return self.characters.get(name)
    
    def create_character(self, name: str, is_player: bool = False, **stats) -> Character:
        """
        Create a new character from scratch.
        
        Args:
            name: Character name
            is_player: Whether this is the player character
            **stats: Initial stats
            
        Returns:
            The created character
        """
        # Create character
        char = Character(name, is_player=is_player, **stats)
        
        # Add to loaded characters
        self.characters[name] = char
        
        # Set as player if marked as such
        if is_player and not self.player_character:
            self.player_character = char
        
        return char
    
    def load_template(self, template_path: str) -> Dict[str, Any]:
        """
        Load a character template file (read-only).
        
        Args:
            template_path: Path to the template file (relative to templates directory or absolute)
            
        Returns:
            Dictionary with template data or empty dict if loading failed
        """
        # Determine full path
        if os.path.isabs(template_path):
            filepath = template_path
        elif self.templates_directory:
            filepath = os.path.join(self.templates_directory, template_path)
        else:
            filepath = template_path
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Template file not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                template_data = json.load(file)
            return template_data
        except Exception as e:
            print(f"Error loading character template '{template_path}': {e}")
            return {}
    
    def create_character_from_template(self, template_path: str, name: str, 
                                       is_player: bool = False, override_stats: Dict[str, Any] = None) -> Optional[Character]:
        """
        Create a character from a template file and apply override stats.
        
        Args:
            template_path: Path to the template file (relative to templates directory or absolute)
            name: Character name (overrides template name)
            is_player: Whether this is a player character (overrides template setting)
            override_stats: Dictionary of stats to override the template values
            
        Returns:
            Character object or None if creation failed
        """
        # Load template data
        template_data = self.load_template(template_path)
        if not template_data:
            return None
        
        try:
            # Extract template stats
            template_stats = template_data.get('stats', {})
            
            # Apply overrides
            final_stats = template_stats.copy()
            if override_stats:
                final_stats.update(override_stats)
            
            # Create character with combined stats
            char = Character(name, is_player=is_player, **final_stats)
            
            # Set inventory (if in template)
            if 'inventory' in template_data:
                char.inventory = template_data['inventory'].copy()
            
            # Set relationships (if in template)
            if 'relationships' in template_data:
                char.relationships = template_data['relationships'].copy()
            
            # Add to loaded characters
            self.characters[name] = char
            
            # Set as player if marked as such
            if is_player and not self.player_character:
                self.player_character = char
            
            return char
        except Exception as e:
            print(f"Error creating character from template '{template_path}': {e}")
            return None
    
    def list_available_templates(self) -> List[str]:
        """
        List all character templates.
        
        Returns:
            List of template filenames (without extension)
        """
        if not self.templates_directory or not os.path.exists(self.templates_directory):
            return []
        
        template_names = []
        for filename in os.listdir(self.templates_directory):
            if filename.endswith('.tchar'):
                template_name = os.path.splitext(filename)[0]
                template_names.append(template_name)
        
        return template_names