# descriptors.py - Modular descriptor system
from typing import Dict, Callable, Any



class DescriptorManager:
    """
    Manages descriptors for characters and game elements.
    Updated to work with DynamicStats.
    """
    def __init__(self):
        self.body_descriptors = {}  # type: Dict[str, Callable[[Any], str]]
        self.energy_descriptors = {}  # type: Dict[str, Callable[[Any], str]]
        self.custom_descriptors = {}  # type: Dict[str, Callable[[Any], str]]
        
        # Load default descriptors
        self._register_default_descriptors()
    
    def _register_default_descriptors(self):
        """Register default descriptor functions."""
        # Body type descriptors
        self.register_body_descriptor('default', self._default_body_descriptor)
        self.register_energy_descriptor('default', self._default_energy_descriptor)
    
    def _default_body_descriptor(self, stats):
        """Default body type descriptor based on BMI and muscle mass."""
        # Calculate BMI if height and weight are available
        bmi = None
        if stats.height is not None and stats.weight is not None:
            height_in_meters = stats.height / 100
            bmi = round(stats.weight / (height_in_meters * height_in_meters), 1)
        
        if bmi is None:
            return "of indeterminate build"
        
        if bmi < 18.5:
            base = "underweight"
        elif bmi < 25:
            base = "average weight"
        elif bmi < 30:
            base = "overweight"
        else:
            base = "obese"
            
        if stats.muscle_mass and stats.muscle_mass > 40:
            base = f"muscular, {base}"
        
        return base
    
    def _default_energy_descriptor(self, stats):
        """Default energy level descriptor."""
        # Check if energy stat exists
        if stats.energy is None:
            return "of unknown energy level"
            
        if stats.energy < 20:
            return "exhausted"
        elif stats.energy < 40:
            return "tired"
        elif stats.energy < 60:
            return "somewhat energetic"
        elif stats.energy < 80:
            return "energetic"
        else:
            return "very energetic"
    
    def register_body_descriptor(self, name: str, descriptor_func: Callable[[Any], str]):
        """Register a body descriptor function."""
        self.body_descriptors[name] = descriptor_func
    
    def register_energy_descriptor(self, name: str, descriptor_func: Callable[[Any], str]):
        """Register an energy descriptor function."""
        self.energy_descriptors[name] = descriptor_func
    
    def register_custom_descriptor(self, name: str, descriptor_func: Callable[[Any], str]):
        """Register a custom descriptor function."""
        self.custom_descriptors[name] = descriptor_func
    
    def get_body_description(self, character, descriptor_name: str = 'default') -> str:
        """Get a description of the character's body."""
        descriptor = self.body_descriptors.get(descriptor_name, self.body_descriptors['default'])
        return descriptor(character.stats)
    
    def get_energy_description(self, character, descriptor_name: str = 'default') -> str:
        """Get a description of the character's energy level."""
        descriptor = self.energy_descriptors.get(descriptor_name, self.energy_descriptors['default'])
        return descriptor(character.stats)
    
    def get_custom_description(self, obj: Any, descriptor_name: str, default: str = "") -> str:
        """Get a description using a custom descriptor."""
        if descriptor_name in self.custom_descriptors:
            return self.custom_descriptors[descriptor_name](obj)
        return default
    
    def describe_character(self, character, 
                          body_descriptor: str = 'default', 
                          energy_descriptor: str = 'default') -> str:
        """Generate a full character description."""
        body_desc = self.get_body_description(character, body_descriptor)
        energy_desc = self.get_energy_description(character, energy_descriptor)
        
        motivation = character.stats.motivation
        motivation_text = ""
        if motivation is not None:
            motivation_text = f" They currently have {motivation:.0f}% motivation."
        
        return f"{character.name} is {body_desc} and appears {energy_desc}.{motivation_text}"