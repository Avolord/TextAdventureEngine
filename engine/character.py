# character.py - Character related classes


class DynamicStats:
    """
    A dynamic dictionary-like class that allows attribute access via dot notation.
    All character parameters are stored here, regardless of source (template or story).
    """
    def __init__(self, **initial_values):
        # Internal dictionary to store all values
        self._data = {}
        
        # Initialize with any provided values
        for key, value in initial_values.items():
            self._data[key] = value
    
    def __getattr__(self, name):
        """Allow attribute access via dot notation (obj.attribute)."""
        # Return None if attribute doesn't exist instead of raising AttributeError
        return self._data.get(name, None)
    
    def __setattr__(self, name, value):
        """Allow setting attributes via dot notation."""
        # Special case for _data which is our internal storage
        if name == '_data':
            super().__setattr__(name, value)
        else:
            # All other attributes go in the _data dictionary
            self._data[name] = value
    
    def __contains__(self, name):
        """Support for 'in' operator (name in stats)."""
        return name in self._data
    
    def get(self, name, default=None):
        """Get an attribute with a default value if it doesn't exist."""
        return self._data.get(name, default)
    
    def set(self, name, value):
        """Set an attribute value."""
        self._data[name] = value
    
    def update(self, **kwargs):
        """Update multiple attributes at once."""
        for key, value in kwargs.items():
            self._data[key] = value
    
    def to_dict(self):
        """Convert to a plain dictionary for serialization."""
        return self._data.copy()
    
    @classmethod
    def from_dict(cls, data):
        """Create from a dictionary."""
        stats = cls()
        stats._data = data.copy()
        return stats


class Character:
    """
    Represents any character in the game (player or NPC).
    All character parameters are stored in the stats object.
    """
    def __init__(self, name: str, is_player: bool = False, **initial_stats):
        self.name = name
        self.is_player = is_player
        
        # Create dynamic stats with initial values
        self.stats = DynamicStats(**initial_stats)
        
        # Initialize other properties
        self.inventory = []
        self.relationships = {}
    
    def update_stats(self, **kwargs):
        """
        Update stats with new values.
        
        Args:
            **kwargs: Key-value pairs to update
        """
        for key, value in kwargs.items():
            # Handle percentage values to keep them within bounds
            if key in ['motivation', 'energy', 'confidence', 'stress', 
                      'happiness', 'body_fat', 'muscle_mass', 'discipline',
                      'health', 'fitness_level', 'positivity', 'empathy', 
                      'expertise', 'supportiveness'] and isinstance(value, (int, float)):
                value = max(0, min(100, value))
            
            # Set the attribute
            setattr(self.stats, key, value)
    
    def has_stat(self, name):
        """Check if a stat exists for this character."""
        return name in self.stats
    
    def get_attribute(self, name, default=None):
        """Get an attribute value with a default if not set."""
        return self.stats.get(name, default)
    
    def set_attribute(self, name, value):
        """Set an attribute value."""
        self.stats.set(name, value)
    
    def describe(self):
        """Generate a basic description of the character."""
        desc_parts = [f"{self.name}"]
        
        # Add description if available
        if self.stats.description:
            desc_parts.append(f"is {self.stats.description}")
        
        # Add height/weight if available
        if self.stats.height and self.stats.weight:
            desc_parts.append(f"({self.stats.height}cm, {self.stats.weight}kg)")
        
        return " ".join(desc_parts)
    
    def to_dict(self):
        """Convert to a dictionary for serialization."""
        return {
            'name': self.name,
            'is_player': self.is_player,
            'stats': self.stats.to_dict(),
            'inventory': self.inventory.copy(),
            'relationships': self.relationships.copy()
        }

    @classmethod
    def from_dict(cls, data):
        """Create from a dictionary."""
        # Create character with basic properties
        char = cls(data['name'], data['is_player'])
        
        # Load stats using DynamicStats.from_dict
        char.stats = DynamicStats.from_dict(data['stats'])
        
        # Copy other properties
        char.inventory = data['inventory'].copy()
        char.relationships = data['relationships'].copy()
        
        return char