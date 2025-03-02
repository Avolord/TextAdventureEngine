# game_state.py - Game state tracking
from dataclasses import dataclass, field
from typing import Callable, Dict, Set, Any, Optional, List
import json

from .character import Character


@dataclass
class GameState:
    """Tracks the current state of the game."""
    current_scene_id: str
    player: Character
    npcs: Dict[str, Character] = field(default_factory=dict)
    visited_scenes: Set[str] = field(default_factory=set)
    completed_events: Set[str] = field(default_factory=set)
    variables: Dict[str, Any] = field(default_factory=dict)
    day: int = 1
    time_of_day: str = "morning"  # morning, afternoon, evening, night
    
    def add_npc(self, npc: Character):
        """Add an NPC to the game state."""
        self.npcs[npc.name] = npc
    
    def get_character(self, name: str) -> Optional[Character]:
        """Get a character by name (player or NPC)."""
        if self.player.name == name:
            return self.player
        return self.npcs.get(name)
    
    def complete_event(self, event_id: str):
        """Mark an event as completed."""
        self.completed_events.add(event_id)
    
    def is_event_completed(self, event_id: str) -> bool:
        """Check if an event has been completed."""
        return event_id in self.completed_events
    
    def set_variable(self, name: str, value: Any):
        """Set a game variable."""
        self.variables[name] = value
    
    def get_variable(self, name: str, default=None) -> Any:
        """Get a game variable, returning default if not found."""
        return self.variables.get(name, default)
    
    def advance_time(self):
        """Move time forward by one period."""
        time_periods = ["morning", "afternoon", "evening", "night"]
        current_index = time_periods.index(self.time_of_day)
        
        if current_index == len(time_periods) - 1:
            # Move to the next day
            self.day += 1
            self.time_of_day = time_periods[0]
            
            # Reset daily stats for all characters
            self._process_daily_updates(self.player)
            for npc in self.npcs.values():
                self._process_daily_updates(npc)
        else:
            # Move to the next time period in the same day
            self.time_of_day = time_periods[current_index + 1]
    
    def _process_daily_updates(self, character: Character):
        """Process daily stat updates for a character."""
        # Reset meals
        character.stats.meals_today = 0
        
        # Get days since exercise (use get_attribute for safety)
        days_since_exercise = character.get_attribute("days_since_exercise", 0)
        character.set_attribute("days_since_exercise", days_since_exercise + 1)
        
        # Reduce motivation slightly if not exercising
        if days_since_exercise > 3:
            character.update_stats(motivation=character.stats.motivation - 2)
        
        # Adjust energy based on sleep
        sleep_hours = character.get_attribute("sleep_hours", 7)
        if sleep_hours < 6:
            character.update_stats(energy=character.stats.energy - 15)
        elif sleep_hours > 8:
            character.update_stats(energy=min(100, character.stats.energy + 10))
            
    def to_dict(self):
        """Convert to a dictionary for serialization."""
        return {
            'current_scene_id': self.current_scene_id,
            'player': self.player.to_dict(),
            'npcs': {name: npc.to_dict() for name, npc in self.npcs.items()},
            'visited_scenes': list(self.visited_scenes),
            'completed_events': list(self.completed_events),
            'variables': self._serialize_variables(),
            'day': self.day,
            'time_of_day': self.time_of_day
        }

    def _serialize_variables(self):
        """
        Serialize variables to JSON-compatible format.
        Handles basic types that can be directly serialized.
        """
        serialized = {}
        for k, v in self.variables.items():
            # Handle basic JSON-compatible types
            if isinstance(v, (str, int, float, bool, type(None))):
                serialized[k] = v
            # Handle lists and dicts if they contain basic types
            elif isinstance(v, (list, dict)):
                try:
                    # Test if JSON serializable
                    json.dumps(v)
                    serialized[k] = v
                except (TypeError, OverflowError):
                    # Skip non-serializable complex objects
                    pass
            # Skip other non-serializable types
        return serialized

    @classmethod
    def from_dict(cls, data):
        """Create from a dictionary."""
        from .character import Character
        
        # Create player character
        player = Character.from_dict(data['player'])
        
        # Create game state with player and current scene
        state = cls(data['current_scene_id'], player)
        
        # Restore simple properties
        state.day = data['day']
        state.time_of_day = data['time_of_day']
        
        # Restore collections (convert lists back to sets)
        state.visited_scenes = set(data['visited_scenes'])
        state.completed_events = set(data['completed_events'])
        
        # Restore variables dictionary
        state.variables = data['variables'].copy()
        
        # Restore NPCs
        for name, npc_data in data['npcs'].items():
            npc = Character.from_dict(npc_data)
            state.npcs[name] = npc
        
        return state


class GameStateManager:
    """
    Manages game state and provides methods to manipulate it.
    """
    def __init__(self):
        self.state: Optional[GameState] = None
        self.actions: Dict[str, Callable[[GameState], str]] = {}  # type: Dict[str, Callable[[GameState], str]]
        self.evaluator = ExpressionEvaluator()
    
    def create_game_state(self, starting_scene: str, player: Character) -> GameState:
        """Create a new game state with the given starting scene and player."""
        self.state = GameState(current_scene_id=starting_scene, player=player)
        self.state.visited_scenes.add(starting_scene)
        return self.state
    
    def register_action(self, action_id: str, handler):
        """Register an action handler function."""
        self.actions[action_id] = handler
    
    def execute_action(self, action_id: str) -> str:
        """Execute an action and return the result text."""
        if action_id in self.actions:
            return self.actions[action_id](self.state)
        return "Nothing happens."
    
    def change_scene(self, scene_id: str):
        """Change the current scene."""
        if self.state:
            self.state.current_scene_id = scene_id
            self.state.visited_scenes.add(scene_id)
    
    def evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string in the context of the current game state."""
        if not condition or not self.state:
            return True
        
        return self.evaluator.evaluate(condition, self.state)


class ExpressionEvaluator:
    """
    Evaluates expressions and conditions in the context of game state.
    """
    def evaluate(self, expression: str, game_state: GameState) -> Any:
        """
        Evaluate an expression string in the context of the game state.
        
        Supported expressions:
        - Simple comparisons: "energy > 50", "day <= 3"
        - Event checks: "has_completed('event_name')"
        - Variable checks: "var('name') == value"
        - Time checks: "time_of_day == 'morning'"
        """
        # Create a context with game state variables
        context = {
            'player': game_state.player,
            'game': game_state,
            'day': game_state.day,
            'time_of_day': game_state.time_of_day,
            'has_completed': lambda event: game_state.is_event_completed(event),
            'var': lambda name, default=None: game_state.get_variable(name, default)
        }
        
        # Add stats for easy access
        for stat_name in dir(game_state.player.stats):
            if not stat_name.startswith('_') and not callable(getattr(game_state.player.stats, stat_name)):
                context[stat_name] = getattr(game_state.player.stats, stat_name)
        
        # Add NPCs to context
        for npc_name, npc in game_state.npcs.items():
            # Create a safe name for the NPC (remove spaces, etc.)
            safe_name = ''.join(c for c in npc_name if c.isalnum())
            context[safe_name] = npc
        
        try:
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, context)
            return result
        except Exception as e:
            # If evaluation fails, return False for conditions
            print(f"Error evaluating expression '{expression}': {e}")
            return False