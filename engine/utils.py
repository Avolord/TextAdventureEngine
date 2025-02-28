# utils.py - Utility functions
import os
import re
import importlib.util
from typing import Dict, Any, List, Optional, Callable


def load_module_from_file(filepath: str, module_name: str = None) -> Optional[Any]:
    """
    Dynamically load a Python module from a file.
    
    Args:
        filepath: Path to the Python file
        module_name: Optional module name, defaults to filename without extension
    
    Returns:
        The loaded module, or None if loading failed
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        # Generate module name from filename if not provided
        if not module_name:
            module_name = os.path.basename(filepath).replace('.py', '')
        
        # Load module
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading module from {filepath}: {e}")
        return None


def safe_eval(expr: str, context: Dict[str, Any], default=None) -> Any:
    """
    Safely evaluate an expression in a given context.
    
    Args:
        expr: Expression to evaluate
        context: Dictionary of variables
        default: Default value to return on error
    
    Returns:
        Result of the evaluation, or default value if evaluation fails
    """
    try:
        # Create a restricted builtins dictionary
        restricted_builtins = {
            'True': True,
            'False': False,
            'None': None,
            'abs': abs,
            'bool': bool,
            'float': float,
            'int': int,
            'len': len,
            'max': max,
            'min': min,
            'round': round,
            'sum': sum,
            'str': str,
        }
        
        # Evaluate expression
        return eval(expr, {"__builtins__": restricted_builtins}, context)
    except Exception as e:
        print(f"Error evaluating expression '{expr}': {e}")
        return default


def format_stat_change(old_value: float, new_value: float, stat_name: str = "stat") -> str:
    """
    Format a stat change for display.
    
    Args:
        old_value: Previous value
        new_value: New value
        stat_name: Name of the stat
    
    Returns:
        Formatted string describing the change
    """
    if old_value == new_value:
        return f"{stat_name.capitalize()} unchanged."
    
    difference = new_value - old_value
    change_type = "increased" if difference > 0 else "decreased"
    abs_diff = abs(difference)
    
    # Format differently based on magnitude
    if abs_diff >= 10:
        intensity = "significantly"
    elif abs_diff >= 5:
        intensity = "notably"
    elif abs_diff >= 2:
        intensity = "somewhat"
    else:
        intensity = "slightly"
    
    return f"{stat_name.capitalize()} {change_type} {intensity} by {abs_diff:.1f}."


def parse_requirements_from_string(requirement_str: str) -> Dict[str, Any]:
    """
    Parse a requirement string into a structured format.
    
    Example input: "energy > 50 and days_since_exercise < 2"
    
    Args:
        requirement_str: String representation of requirements
    
    Returns:
        Dictionary of parsed requirements
    """
    # Simple parsing logic - can be expanded for more complex requirements
    requirements = {}
    
    # Look for patterns like "stat_name operator value"
    pattern = r'(\w+)\s*([><!=]+)\s*(\d+(?:\.\d+)?)'
    
    for match in re.finditer(pattern, requirement_str):
        stat_name, operator, value = match.groups()
        
        # Convert value to appropriate type
        if '.' in value:
            value = float(value)
        else:
            value = int(value)
        
        requirements[stat_name] = {'operator': operator, 'value': value}
    
    return requirements


def evaluate_requirements(character, requirements: Dict[str, Any]) -> bool:
    """
    Evaluate if a character meets the given requirements.
    
    Args:
        character: Character to check
        requirements: Dictionary of requirements
    
    Returns:
        True if all requirements are met, False otherwise
    """
    for stat_name, req in requirements.items():
        # Get the stat value
        if hasattr(character.stats, stat_name):
            stat_value = getattr(character.stats, stat_name)
        else:
            # Check if it's a custom attribute
            stat_value = character.get_attribute(stat_name)
            if stat_value is None:
                # Requirement not met if attribute doesn't exist
                return False
        
        # Evaluate the requirement
        op = req['operator']
        val = req['value']
        
        if op == '>' and not (stat_value > val):
            return False
        elif op == '>=' and not (stat_value >= val):
            return False
        elif op == '<' and not (stat_value < val):
            return False
        elif op == '<=' and not (stat_value <= val):
            return False
        elif op == '==' and not (stat_value == val):
            return False
        elif op == '!=' and not (stat_value != val):
            return False
    
    # All requirements were met
    return True