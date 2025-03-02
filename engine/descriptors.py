# descriptors.py - Enhanced modular descriptor system
from typing import Dict, Callable, Any, Optional, Set



class DescriptorManager:
    """
    Manages descriptors for characters and game elements.
    Updated to work with DynamicStats and support character-specific descriptors.
    """
    def __init__(self):
        self.body_descriptors = {}  # type: Dict[str, Callable[[Any], str]]
        self.energy_descriptors = {}  # type: Dict[str, Callable[[Any], str]]
        self.custom_descriptors = {}  # type: Dict[str, Callable[[Any], str]]
        
        # Track which descriptor is used by each character
        self.character_body_descriptors = {}  # type: Dict[str, str]
        self.character_energy_descriptors = {}  # type: Dict[str, str]
        
        # Track registered descriptor names for script auto-completion
        self.registered_descriptors = {
            'body': set(),
            'energy': set(),
            'custom': set()
        }  # type: Dict[str, Set[str]]
        
        # Load default descriptors
        self._register_default_descriptors()
    
    def _register_default_descriptors(self):
        """Register default descriptor functions."""
        # Body type descriptors
        self.register_body_descriptor('default', self._default_body_descriptor)
        self.register_body_descriptor('fitness', self._fitness_body_descriptor)
        self.register_body_descriptor('simple', self._simple_body_descriptor)
        
        # Energy descriptors
        self.register_energy_descriptor('default', self._default_energy_descriptor)
        self.register_energy_descriptor('detailed', self._detailed_energy_descriptor)
        self.register_energy_descriptor('simple', self._simple_energy_descriptor)
    
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
    
    def _fitness_body_descriptor(self, stats):
        """Fitness-focused body descriptor that emphasizes muscle and fitness levels."""
        if not stats.fitness_level:
            return "of unknown fitness level"
            
        if stats.fitness_level < 20:
            fitness = "out of shape"
        elif stats.fitness_level < 40:
            fitness = "somewhat fit"
        elif stats.fitness_level < 60:
            fitness = "fairly fit"
        elif stats.fitness_level < 80:
            fitness = "very fit"
        else:
            fitness = "extremely fit"
        
        # Add muscle mass qualifier if available
        if stats.muscle_mass:
            if stats.muscle_mass < 20:
                return f"{fitness} with little muscle definition"
            elif stats.muscle_mass < 40:
                return f"{fitness} with moderate muscle tone"
            elif stats.muscle_mass < 60:
                return f"{fitness} with well-defined muscles"
            else:
                return f"{fitness} with impressive musculature"
        
        return fitness
    
    def _simple_body_descriptor(self, stats):
        """Simple body descriptor with minimal detail."""
        if stats.height and stats.weight:
            height_in_meters = stats.height / 100
            bmi = round(stats.weight / (height_in_meters * height_in_meters), 1)
            
            if bmi < 20:
                return "thin"
            elif bmi < 25:
                return "average build"
            elif bmi < 30:
                return "heavyset"
            else:
                return "large"
        
        return "of average build"
    
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
    
    def _detailed_energy_descriptor(self, stats):
        """More detailed energy descriptor that includes motivation."""
        # Base energy description
        if stats.energy is None:
            energy_desc = "of unknown energy level"
        elif stats.energy < 20:
            energy_desc = "completely drained"
        elif stats.energy < 40:
            energy_desc = "noticeably fatigued"
        elif stats.energy < 60:
            energy_desc = "moderately energetic"
        elif stats.energy < 80:
            energy_desc = "quite energetic"
        else:
            energy_desc = "bursting with energy"
            
        # Add motivation if available
        if stats.motivation is not None:
            if stats.motivation < 30:
                return f"{energy_desc} but unmotivated"
            elif stats.motivation < 60:
                return f"{energy_desc} and somewhat motivated"
            else:
                return f"{energy_desc} and highly motivated"
        
        return energy_desc
    
    def _simple_energy_descriptor(self, stats):
        """Simplified energy descriptor."""
        if stats.energy is None:
            return "neutral"
        
        if stats.energy < 30:
            return "tired"
        elif stats.energy < 70:
            return "alert"
        else:
            return "energetic"
    
    def register_body_descriptor(self, name: str, descriptor_func: Callable[[Any], str]):
        """Register a body descriptor function."""
        self.body_descriptors[name] = descriptor_func
        self.registered_descriptors['body'].add(name)
    
    def register_energy_descriptor(self, name: str, descriptor_func: Callable[[Any], str]):
        """Register an energy descriptor function."""
        self.energy_descriptors[name] = descriptor_func
        self.registered_descriptors['energy'].add(name)
    
    def register_custom_descriptor(self, name: str, descriptor_func: Callable[[Any], str]):
        """Register a custom descriptor function."""
        self.custom_descriptors[name] = descriptor_func
        self.registered_descriptors['custom'].add(name)
    
    def set_character_body_descriptor(self, character_name: str, descriptor_name: str = 'default'):
        """
        Set which body descriptor to use for a specific character.
        
        Args:
            character_name: Name of the character
            descriptor_name: Name of the descriptor to use
        """
        if descriptor_name in self.body_descriptors:
            self.character_body_descriptors[character_name] = descriptor_name
            return True
        return False
    
    def set_character_energy_descriptor(self, character_name: str, descriptor_name: str = 'default'):
        """
        Set which energy descriptor to use for a specific character.
        
        Args:
            character_name: Name of the character
            descriptor_name: Name of the descriptor to use
        """
        if descriptor_name in self.energy_descriptors:
            self.character_energy_descriptors[character_name] = descriptor_name
            return True
        return False
    
    def get_character_body_descriptor_name(self, character_name: str) -> str:
        """Get the name of the body descriptor used for a character."""
        return self.character_body_descriptors.get(character_name, 'default')
    
    def get_character_energy_descriptor_name(self, character_name: str) -> str:
        """Get the name of the energy descriptor used for a character."""
        return self.character_energy_descriptors.get(character_name, 'default')
    
    def get_body_description(self, character, descriptor_name: str = None) -> str:
        """
        Get a description of the character's body.
        
        Args:
            character: Character object
            descriptor_name: Optional override for descriptor to use
            
        Returns:
            Description string
        """
        # Determine which descriptor to use
        if descriptor_name is None:
            descriptor_name = self.character_body_descriptors.get(character.name, 'default')
        
        # Get the descriptor function
        descriptor = self.body_descriptors.get(descriptor_name, self.body_descriptors['default'])
        return descriptor(character.stats)
    
    def get_energy_description(self, character, descriptor_name: str = None) -> str:
        """
        Get a description of the character's energy level.
        
        Args:
            character: Character object
            descriptor_name: Optional override for descriptor to use
            
        Returns:
            Description string
        """
        # Determine which descriptor to use
        if descriptor_name is None:
            descriptor_name = self.character_energy_descriptors.get(character.name, 'default')
        
        # Get the descriptor function
        descriptor = self.energy_descriptors.get(descriptor_name, self.energy_descriptors['default'])
        return descriptor(character.stats)
    
    def get_custom_description(self, obj: Any, descriptor_name: str, default: str = "") -> str:
        """Get a description using a custom descriptor."""
        if descriptor_name in self.custom_descriptors:
            return self.custom_descriptors[descriptor_name](obj)
        return default
    
    def describe_character(self, character, 
                          body_descriptor: str = None, 
                          energy_descriptor: str = None) -> str:
        """
        Generate a full character description.
        
        Args:
            character: Character object
            body_descriptor: Optional override for body descriptor
            energy_descriptor: Optional override for energy descriptor
            
        Returns:
            Full character description
        """
        body_desc = self.get_body_description(character, body_descriptor)
        energy_desc = self.get_energy_description(character, energy_descriptor)
        
        motivation = character.stats.motivation
        motivation_text = ""
        if motivation is not None:
            motivation_text = f" They currently have {motivation:.0f}% motivation."
        
        return f"{character.name} is {body_desc} and appears {energy_desc}.{motivation_text}"
    
    def get_available_descriptors(self, descriptor_type: str = None) -> Dict[str, Set[str]]:
        """
        Get all available descriptor names by type.
        
        Args:
            descriptor_type: Optional type to filter ('body', 'energy', 'custom')
            
        Returns:
            Dictionary of descriptor types and names
        """
        if descriptor_type:
            return {descriptor_type: self.registered_descriptors.get(descriptor_type, set())}
        return self.registered_descriptors