# scene.py - Updated scene handling with story transitions
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional


@dataclass
class Choice:
    """A choice the player can make."""
    text: str  # Text shown to the player
    action_id: Optional[str] = None  # Identifier for the action
    next_scene: Optional[str] = None  # ID of scene to transition to
    condition: Optional[str] = None  # Condition string to be evaluated at runtime
    next_story: Optional[str] = None  # ID of story to transition to
    
    def __post_init__(self):
        # Ensure action_id is None rather than empty string
        if self.action_id == "":
            self.action_id = None


class Scene:
    """
    Represents a scene in the game story.
    """
    def __init__(self, scene_id: str, title: str = "", content: str = ""):
        self.scene_id = scene_id
        self.title = title
        self.content = content
        self.choices = []  # List of Choice objects
    
    def add_choice(self, choice: Choice):
        """Add a choice to this scene."""
        self.choices.append(choice)
    
    def add_simple_choice(self, text: str, action_id: str = None, next_scene: str = None, 
                         condition: str = None, next_story: str = None):
        """Convenience method to add a choice with minimal parameters."""
        choice = Choice(text, action_id, next_scene, condition)
        if next_story:
            choice.next_story = next_story
        self.choices.append(choice)


class SceneManager:
    """
    Manages all scenes in the game.
    """
    def __init__(self):
        self.scenes = {}  # type: Dict[str, Scene]
    
    def add_scene(self, scene: Scene):
        """Add a scene to the manager."""
        self.scenes[scene.scene_id] = scene
    
    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """Get a scene by ID."""
        return self.scenes.get(scene_id)
    
    def create_scene(self, scene_id: str, title: str, content: str) -> Scene:
        """Create and add a new scene."""
        scene = Scene(scene_id, title, content)
        self.add_scene(scene)
        return scene
    
    def clear(self):
        """Clear all scenes."""
        self.scenes = {}
    
    def has_scene(self, scene_id: str) -> bool:
        """Check if a scene exists."""
        return scene_id in self.scenes
    
    def get_all_scene_ids(self) -> List[str]:
        """Get a list of all scene IDs."""
        return list(self.scenes.keys())
    
    def add_simple_choice_to_scene(self, scene_id: str, text: str, action_id: str = None, next_scene: str = None, 
                            condition: str = None, next_story: str = None):
        """Add a choice to a scene by ID."""
        scene = self.get_scene(scene_id)
        if scene:
            scene.add_simple_choice(text, action_id, next_scene, condition, next_story)
        else:
            raise ValueError(f"Scene '{scene_id}' not found")
        
    def add_choice_to_scene(self, scene_id: str, choice: Choice):
        """Add a choice to a scene by ID."""
        scene = self.get_scene(scene_id)
        if scene:
            scene.add_choice(choice)
        else:
            raise ValueError(f"Scene '{scene_id}' not found")