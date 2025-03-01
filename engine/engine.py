# engine.py - Updated without save system
import re
import os
from typing import Dict, List, Any, Optional, Callable, Set, Tuple

from .character import Character
from .scene import SceneManager, Scene, Choice
from .game_state import GameStateManager
from .parser import StoryParser
from .descriptors import DescriptorManager
from .character_manager import CharacterManager

from .template_processor import TemplateProcessor, TemplateResult

class TextAdventureEngine:
    """
    Main game engine that coordinates all components.
    """
    def __init__(self):
        self.title = "Text Adventure"
        self.scene_manager = SceneManager()
        self.game_state_manager = GameStateManager()
        self.parser = StoryParser(self.scene_manager)
        self.descriptor_manager = DescriptorManager()
        self.character_manager = CharacterManager()
        self.starting_scene = "start"
        self.story_paths = {}  # Map of story IDs to file paths
        self.current_story_id = None
        self.stories_directory = None
        self.template_processor = TemplateProcessor()
        self._scene_cache = {}  # Cache for processed scenes
    
    def set_directories(self, stories_dir: str, templates_dir: str):
        """
        Set all directory paths for the engine.
        
        Args:
            stories_dir: Path to the stories directory
            templates_dir: Path to the character templates directory
        """
        # Create directories if they don't exist
        os.makedirs(stories_dir, exist_ok=True)
        os.makedirs(templates_dir, exist_ok=True)
        
        # Set directories for components
        self.set_stories_directory(stories_dir)
        self.character_manager.set_templates_directory(templates_dir)
    
    def set_stories_directory(self, directory_path: str):
        """Set the directory where stories are stored."""
        self.stories_directory = directory_path
        
        # Scan directory for stories
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                if filename.endswith('.tadv'):
                    story_id = os.path.splitext(filename)[0]
                    self.story_paths[story_id] = os.path.join(directory_path, filename)
    
    def load_story(self, filepath_or_id: str):
        """
        Load a story file and initialize the game components.
        
        Args:
            filepath_or_id: Path to the story file (.tadv) or story ID
        
        Returns:
            bool: True if loading was successful
        """
        # Determine if this is a filepath or a story ID
        if filepath_or_id in self.story_paths:
            filepath = self.story_paths[filepath_or_id]
            story_id = filepath_or_id
        elif os.path.exists(filepath_or_id):
            filepath = filepath_or_id
            story_id = os.path.splitext(os.path.basename(filepath_or_id))[0]
        elif (self.stories_directory and 
              os.path.exists(os.path.join(self.stories_directory, filepath_or_id + '.tadv'))):
            filepath = os.path.join(self.stories_directory, filepath_or_id + '.tadv')
            story_id = filepath_or_id
        else:
            print(f"Story not found: {filepath_or_id}")
            return False
        
        try:
            # Reset scene manager if loading a new story
            if self.current_story_id != story_id:
                self.scene_manager = SceneManager()
                self.parser = StoryParser(self.scene_manager)
            
            # Parse story file
            metadata = self.parser.parse_file(filepath)
            
            # Set title and starting scene from metadata
            if 'title' in metadata:
                self.title = metadata['title']
            
            if 'start' in metadata:
                self.starting_scene = metadata['start']
            
            # Process imports if any
            for import_path in self.parser.imports:
                self._process_import(import_path)
            
            # Execute functions code to register actions
            self._register_functions(self.parser.get_functions_code())
            
            # Set current story ID
            self.current_story_id = story_id
            
            return True
        
        except Exception as e:
            print(f"Error loading story: {e}")
            return False
    
    def _process_import(self, import_path: str):
        """
        Process an import directive.
        
        Args:
            import_path: Path to the imported file
        """
        # Determine the full path to the imported file
        if os.path.isabs(import_path):
            filepath = import_path
        elif self.stories_directory:
            filepath = os.path.join(self.stories_directory, import_path)
        else:
            filepath = import_path
        
        # Check if the file exists
        if not os.path.exists(filepath):
            print(f"Import file not found: {filepath}")
            return
        
        # Parse the imported file
        if filepath.endswith('.tadv'):
            # This is a full story file - parse normally but don't reset
            self.parser.parse_file(filepath, reset=False)
        elif filepath.endswith('.tscene'):
            # This is a scene file - parse scenes only
            self.parser.parse_scene_file(filepath)
    
    def _register_functions(self, functions_code: str):
        """
        Register functions from the story file.
        
        Args:
            functions_code: Python code defining functions
        """
        if not functions_code:
            return
        
        # Create a namespace for the functions
        namespace = {
            'game': self,  # Allow functions to access the game engine
            'register_action': self.game_state_manager.register_action,
        }
        
        try:
            # Execute the code within this namespace
            exec(functions_code, namespace)
        except Exception as e:
            print(f"Error registering functions: {e}")
    
    def transition_to_story(self, story_id: str, starting_scene: Optional[str] = None):
        """
        Transition to another story, maintaining player state.
        
        Args:
            story_id: ID of the story to transition to
            starting_scene: Optional specific scene to start at
        
        Returns:
            bool: True if transition was successful
        """
        # Check if the story exists
        if story_id not in self.story_paths:
            print(f"Story not found: {story_id}")
            return False
        
        # Save current player state
        saved_player = self.game_state_manager.state.player
        
        # Load the new story
        if not self.load_story(story_id):
            return False
        
        # Initialize the game with the saved player
        return self.initialize_game(starting_scene=starting_scene, keep_player=True)
    
    def initialize_game(self, player_name: str = None, starting_scene: str = None, keep_player: bool = False):
        """
        Initialize a new game.
        
        Args:
            player_name: Optional custom player name
            starting_scene: Optional specific scene to start at
            keep_player: Whether to keep the existing player character
            
        Returns:
            bool: True if initialization was successful
        """
        try:
            player = None
            
            # Use existing player if keep_player is True
            if keep_player and self.game_state_manager.state:
                player = self.game_state_manager.state.player
            else:
                # Process characters defined in the story
                player_data = None
                
                # Find player character data from story
                for name, char_info in self.parser.get_character_data().items():
                    char_data = char_info.get("data", {})
                    is_player = char_data.get('is_player', False)
                    
                    if is_player or name == player_name:
                        player_data = char_info
                        player_name_from_story = name
                        break
                
                # Create player character
                if player_data:
                    # Use player from story
                    if player_data.get("import"):
                        # Import from template with overrides
                        player = self.character_manager.create_character_from_template(
                            player_data["import"],
                            player_name or player_name_from_story,
                            True,  # is_player
                            player_data["data"]
                        )
                    else:
                        # Create from story data
                        player = self.character_manager.create_character(
                            player_name or player_name_from_story, 
                            is_player=True, 
                            **player_data["data"]
                        )
                elif player_name:
                    # Create new player with provided name
                    player = self.character_manager.create_character(player_name, is_player=True)
            
            # Create default player if still none
            if not player:
                player = self.character_manager.create_character("Player", is_player=True)
            
            # Use specified starting scene or default
            scene_id = starting_scene or self.starting_scene
            
            # Create game state
            self.game_state_manager.create_game_state(scene_id, player)
            
            # Create NPCs
            for name, char_info in self.parser.get_character_data().items():
                char_data = char_info.get("data", {})
                is_player = char_data.get('is_player', False)
                
                # Skip player character
                if is_player or name == player.name:
                    continue
                    
                # Create NPC
                if char_info.get("import"):
                    # Import from template with overrides
                    npc = self.character_manager.create_character_from_template(
                        char_info["import"],
                        name,
                        False,  # not a player
                        char_info["data"]
                    )
                else:
                    # Create from story data
                    npc = self.character_manager.create_character(
                        name, 
                        is_player=False, 
                        **char_info["data"]
                    )
                
                # Add to game state
                self.game_state_manager.state.add_npc(npc)
            
            return True
        except Exception as e:
            print(f"Error initializing game: {e}")
            return False
        
    def get_current_scene_info(self):
        """
        Get processed scene information including text and available choices.
        This is the single processing point for a scene.
        
        Returns:
            TemplateResult: Processed scene information
        """
        scene = self.get_current_scene()
        if not scene:
            return TemplateResult("Error: No current scene.")
        
        # Check if scene is already in cache
        scene_id = scene.scene_id
        if scene_id in self._scene_cache:
            # Get cached result
            return self._scene_cache[scene_id]
        
        # Create context for template processing
        context = self._create_template_context()
        
        # Process the scene content once to get both text and choices
        result = self.template_processor.process(scene.content, context)
        
        # Process regular scene choices
        available_choices = []
        for choice in scene.choices:
            # Skip if choice has a condition that evaluates to False
            if choice.condition:
                try:
                    condition_result = self.game_state_manager.evaluate_condition(choice.condition)
                    if not condition_result:
                        continue
                except Exception as e:
                    print(f"Error evaluating condition '{choice.condition}': {e}")
                    continue
            
            # Process template tags in choice text
            processed_text = self.template_processor.process_text(choice.text, context)
            
            # Create a new choice with processed text
            processed_choice = Choice(
                processed_text,
                choice.action_id,
                choice.next_scene,
                None,  # We've already evaluated the condition
                choice.next_story
            )
            
            available_choices.append(processed_choice)
        
        # Add choices from conditional blocks
        template_choices = []
        for choice_data in result.choices:
            choice = Choice(
                choice_data.text,
                choice_data.action_id,
                choice_data.next_scene,
                None,
                choice_data.next_story
            )
            template_choices.append(choice)
        
        # Create a combined result
        combined_result = TemplateResult(result.text, available_choices + template_choices)
        
        # Cache the result
        self._scene_cache[scene_id] = combined_result
        
        return combined_result
    
    def _create_template_context(self):
        """
        Create a context dictionary for template processing.
        
        Returns:
            dict: Context with game state variables
        """
        game_state = self.game_state_manager.state
        
        # Create basic context
        context = {
            'player': game_state.player,
            'game': game_state,
            'var': lambda name, default=None: game_state.get_variable(name, default),
            'describe': lambda char_name: self.descriptor_manager.describe_character(
                game_state.get_character(char_name)
            ),
            'has_completed': lambda event: game_state.is_event_completed(event),
        }
        
        # Add NPCs to context
        for npc_name, npc in game_state.npcs.items():
            safe_name = ''.join(c for c in npc_name if c.isalnum())
            context[safe_name] = npc
        
        return context
    
    def get_current_scene(self) -> Optional[Scene]:
        """Get the current scene."""
        if not self.game_state_manager.state:
            return None
        
        scene_id = self.game_state_manager.state.current_scene_id
        return self.scene_manager.get_scene(scene_id)
    
    def get_current_scene_text(self) -> str:
        """Get the processed text of the current scene."""
        result = self.get_current_scene_info()
        return result.text
    
    def get_available_choices(self) -> List[Choice]:
        """
        Get available choices for the current scene.
        
        Returns:
            List of Choice objects
        """
        result = self.get_current_scene_info()
        return result.choices
    
    def get_choice_texts(self) -> List[str]:
        """
        Get the text of available choices for the current scene.
        
        Returns:
            List of choice texts
        """
        choices = self.get_available_choices()
        return [choice.text for choice in choices]
    
    def _extract_conditional_choices(self, processed_content: str) -> List[Choice]:
        """
        Extract choices from processed content that came from conditional blocks.
        
        Args:
            processed_content: Processed scene content
            
        Returns:
            List of Choice objects
        """
        choices = []
        
        # Extract lines that start with '*' (choices)
        for line in processed_content.split('\n'):
            line = line.strip()
            if line.startswith('*'):
                choice_text = line[1:].strip()
                
                # Check if there's an action/goto
                if '->' in choice_text:
                    text, action_data = choice_text.split('->', 1)
                    text = text.strip()
                    action_data = action_data.strip()
                    
                    # Parse action data
                    action_id = None
                    next_scene = None
                    next_story = None
                    
                    # Extract action_id if present (text before any keywords)
                    action_parts = action_data.split()
                    action_id_parts = []
                    
                    for part in action_parts:
                        if part.startswith(('goto:', 'story:')):
                            break
                        action_id_parts.append(part)
                    
                    if action_id_parts:
                        action_id = ' '.join(action_id_parts)
                    
                    # Check for goto
                    goto_match = re.search(r'goto:(\w+)', action_data)
                    if goto_match:
                        next_scene = goto_match.group(1)
                    
                    # Check for story transition
                    story_match = re.search(r'story:(\w+)(?::(\w+))?', action_data)
                    if story_match:
                        next_story = story_match.group(1)
                        if story_match.group(2):  # Optional scene in new story
                            next_scene = story_match.group(2)
                    
                    # Create choice
                    choice = Choice(text, action_id, next_scene, None, next_story)
                    choices.append(choice)
                else:
                    # Simple choice with just text
                    choice = Choice(choice_text, None, None, None, None)
                    choices.append(choice)
        
        return choices
    
    def handle_choice(self, choice_index: int) -> str:
        """
        Handle the player making a choice.
        
        Args:
            choice_index: Index of the chosen choice
            
        Returns:
            str: Result text
        """
        # Get available choices
        available_choices = self.get_available_choices()
        
        # Check if choice index is valid
        if choice_index < 0 or choice_index >= len(available_choices):
            return "Invalid choice."
        
        # Get the selected choice
        choice = available_choices[choice_index]
        
        # Clear the scene cache when making a choice
        self._scene_cache = {}
        
        # Check for story transition
        if choice.next_story:
            if self.transition_to_story(choice.next_story, choice.next_scene):
                # Return the new scene text
                return self.get_current_scene_text()
            else:
                return f"Failed to transition to story: {choice.next_story}"
        
        # Execute the associated action
        result = ""
        if choice.action_id:
            result = self.game_state_manager.execute_action(choice.action_id)
        
        # Handle scene transition if specified
        if choice.next_scene:
            self.game_state_manager.change_scene(choice.next_scene)
            
            # If no result text was returned, show the new scene text
            if not result:
                result = ""#self.get_current_scene_text()
        
        return result or "You made your choice."
    
    def process_text_command(self, command: str) -> str:
        """
        Process a text command from the player.
        
        Args:
            command: Command text
            
        Returns:
            str: Result of the command
        """
        command = command.strip().lower()
        
        # Split command into parts
        parts = command.split()
        
        if not parts:
            return "Please enter a command."
        
        # Process commands
        cmd = parts[0]
        
        # Help command
        if cmd == "help":
            return (
                "Available commands:\n"
                "- help: Show this help message\n"
            )
        
        # Unknown command
        else:
            return f"Unknown command: {cmd}"
