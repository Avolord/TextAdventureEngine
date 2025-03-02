import os
import re
from typing import TextIO, Dict, List, Any, Optional, Set
from engine.scene import SceneManager

class StoryParser:
    """
    Parser for story files (.tadv) and scene files (.tscene).
    Supports character imports with the @ syntax.
    """
    def __init__(self, scene_manager: SceneManager):
        self.scene_manager: SceneManager = scene_manager
        self.metadata = {}  # type: Dict[str, str]
        self.characters = {}  # type: Dict[str, Dict[str, Any]]
        self.functions_code = ""  # Raw function code to be executed later
        self.imports = set()  # type: Set[str]
        
    def parse_file(self, filepath: str, reset: bool = True) -> Dict[str, Any]:
        """
        Parse a story file and return the metadata.
        
        Args:
            filepath: Path to the story file
            reset: Whether to reset parser state before parsing
        
        Returns:
            Dict[str, Any]: Story metadata
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Story file not found: {filepath}")
        
        # Reset state if requested
        if reset:
            self.metadata = {}
            self.characters = {}
            self.functions_code = ""
            self.imports = set()
        
        with open(filepath, 'r', encoding='utf-8') as file:
            self._parse_content(file)
        
        return self.metadata
    
    def parse_scene_file(self, filepath: str) -> bool:
        """
        Parse a scene file (.tscene) containing only scene definitions.
        
        Args:
            filepath: Path to the scene file
        
        Returns:
            bool: True if parsing was successful
        """
        if not os.path.exists(filepath):
            print(f"Scene file not found: {filepath}")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                self._parse_scenes(file)
            return True
        except Exception as e:
            print(f"Error parsing scene file {filepath}: {e}")
            return False
    
    def _parse_content(self, file: TextIO):
        """Parse the content of a story file."""
        section = None
        content_buffer = []
        
        for line_num, line in enumerate(file, 1):
            line = line.rstrip()
            
            # Skip comments and empty lines
            if line.startswith('#') or not line.strip():
                continue
            
            # Check for import directives
            if line.startswith('@import'):
                parts = line.split(None, 1)
                if len(parts) > 1:
                    import_path = parts[1].strip()
                    self.imports.add(import_path)
                continue
            
            # Check for section headers
            if line.startswith('===') and line.endswith('==='):
                # Process previous section if exists
                if section:
                    self._process_section(section, content_buffer)
                    content_buffer = []
                
                # Set new section
                section = line.strip('= ').lower()
                continue
            
            # Collect lines
            content_buffer.append(line)
        
        # Process the last section
        if section:
            self._process_section(section, content_buffer)
    
    def _parse_scenes(self, file: TextIO):
        """Parse scenes from a file containing only scene definitions."""
        content_buffer = []
        
        for line in file:
            line = line.rstrip()
            
            # Skip comments and empty lines
            if line.startswith('#') or not line.strip():
                continue
            
            # Check for functions section in scene file
            if line.startswith('===') and line.endswith('==='):
                section = line.strip('= ').lower()
                
                # Handle functions in scene files
                if section == 'functions':
                    functions_buffer = []
                    for inner_line in file:
                        inner_line = inner_line.rstrip()
                        
                        # End of functions section
                        if inner_line.startswith('==='):
                            # Process the functions
                            self.functions_code += "\n" + "\n".join(functions_buffer)
                            
                            # Start collecting scene content
                            content_buffer.append(inner_line)
                            break
                        
                        functions_buffer.append(inner_line)
                continue
            
            # Add line to buffer
            content_buffer.append(line)
        
        # Process all scene content
        if content_buffer:
            self._process_section('scene', content_buffer)
    
    def _process_section(self, section: str, content: List[str]):
        """Process a section of the story file."""
        if section == 'metadata':
            self._process_metadata(content)
        elif section == 'characters':
            self._process_characters(content)
        elif section == 'functions':
            self.functions_code = '\n'.join(content)
        elif section == 'scene':
            self._process_scenes(content)
    
    def _process_metadata(self, content: List[str]):
        """Process metadata section."""
        for line in content:
            if ':' in line:
                key, value = line.split(':', 1)
                self.metadata[key.strip().lower()] = value.strip()
    
    def _process_characters(self, content: List[str]):
        """
        Process characters section with import capability.
        Supports syntax like:
        - Player@player.tchar
           health: 100.0
           fitness_level: 30.0
        """
        current_char = None
        char_data = {}
        import_file = None
        
        for line in content:
            # Skip empty lines
            if not line.strip():
                continue
                
            if line.startswith('-'):
                # Process previous character if exists
                if current_char and (char_data or import_file is not None):
                    self.characters[current_char] = {"data": char_data, "import": import_file}
                
                # Start new character
                _, char_declaration = line.split('-', 1)
                char_declaration = char_declaration.strip()
                
                # Check for import syntax
                if '@' in char_declaration:
                    # Format: - Name@template.tchar
                    name, import_path = char_declaration.split('@', 1)
                    current_char = name.strip()
                    import_file = import_path.strip()
                else:
                    # Regular character declaration (with or without attributes)
                    if ':' in char_declaration:
                        current_char = char_declaration.split(':', 1)[0].strip()
                    else:
                        current_char = char_declaration
                    import_file = None
                    
                char_data = {}
                
            elif ':' in line and current_char:
                # Character attribute (either imported or direct)
                # Indentation before attribute is optional but expected for readability
                line = line.strip()
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Convert numeric values
                try:
                    if '.' in value and any(c.isdigit() for c in value):
                        value = float(value)
                    elif value.isdigit():
                        value = int(value)
                    else:
                        # Handle boolean values
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                except ValueError:
                    # Keep as string if conversion fails
                    pass
                
                char_data[key] = value
        
        # Process the last character
        if current_char and (char_data or import_file is not None):
            self.characters[current_char] = {"data": char_data, "import": import_file}
    
    def _process_scenes(self, content: List[str]):
        """Process scenes section."""
        current_scene = None
        scene_buffer = []
        inside_conditional = 0  # Track conditional nesting level
        auto_transition = None
        transition_text = None
        
        for line_num, line in enumerate(content, 1):
            # Check for auto-transition directive
            if line.strip().startswith("@goto:"):
                # Format: @goto:scene_id [transition text]
                directive = line.strip()[6:].strip()
                if " " in directive:
                    scene_id, text = directive.split(" ", 1)
                    auto_transition = scene_id.strip()
                    transition_text = text.strip()
                else:
                    auto_transition = directive.strip()
                    transition_text = None
                continue
            
            # Check for conditional blocks
            if '{%' in line and '%}' in line:
                if 'if ' in line or 'elif ' in line:
                    inside_conditional += 1
                elif 'endif' in line:
                    inside_conditional -= 1
            
            # Check for scene header
            if line.startswith('---') and ':' in line:
                # Process previous scene if exists
                if current_scene and scene_buffer:
                    current_scene.content = '\n'.join(scene_buffer)
                    
                    # Set auto-transition if one was specified
                    if auto_transition:
                        current_scene.set_auto_transition(auto_transition, transition_text)
                        auto_transition = None
                        transition_text = None
                    
                    scene_buffer = []
                
                # Parse scene header
                _, scene_data = line.split('---', 1)
                if ':' in scene_data:
                    scene_id, scene_title = scene_data.split(':', 1)
                    scene_id = scene_id.strip()
                    scene_title = scene_title.strip()
                    
                    # Create new scene
                    current_scene = self.scene_manager.create_scene(scene_id, scene_title, "")
                else:
                    print(f"Warning: Invalid scene header format at line {line_num}")
                    current_scene = None
            
            # Check for choice
            elif line.startswith('*') and current_scene:
                # Skip choices inside conditionals - they'll be processed at runtime
                # Just add them to the scene content
                if inside_conditional > 0:
                    scene_buffer.append(line)
                    continue
                
                choice_text = line[1:].strip()
                if '->' in choice_text:
                    # Split choice text and action
                    text, action_data = choice_text.split('->', 1)
                    text = text.strip()
                    action_data = action_data.strip()
                    
                    # Parse action data
                    action_id = None
                    next_scene = None
                    next_story = None
                    condition = None
                    
                    # Check for goto with conditions
                    # Format: goto:scene1 if condition else goto:scene2
                    if_else_goto_match = re.search(r'goto:(\w+)\s+if\s+(.+?)\s+else\s+goto:(\w+)', action_data)
                    if if_else_goto_match:
                        # This is a conditional goto, store the condition
                        scene1 = if_else_goto_match.group(1)
                        condition_text = if_else_goto_match.group(2)
                        scene2 = if_else_goto_match.group(3)
                        
                        # Create a simple condition to evaluate at runtime
                        condition = f"{condition_text}"
                        
                        # For now, just use the first scene - the condition will be checked at runtime
                        next_scene = scene1
                        
                        # Remove the conditional goto part from action_data to avoid double-processing
                        action_data = action_data.replace(if_else_goto_match.group(0), '')
                    else:
                        # Extract action_id if present (text before any keywords)
                        action_parts = action_data.split()
                        action_id_parts = []
                        
                        for part in action_parts:
                            if part.startswith(('goto:', 'story:', 'if')):
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
                        
                        # Check for conditions
                        if_match = re.search(r'if\s+(.+?)(?:\s+else\s+|$)', action_data)
                        if if_match:
                            condition = if_match.group(1).strip()
                    
                    # Add choice to current scene
                    self.scene_manager.add_simple_choice_to_scene(
                        current_scene.scene_id,
                        text,
                        action_id,
                        next_scene,
                        condition,
                        next_story
                    )
                else:
                    # Simple choice with just text, add it without actions
                    self.scene_manager.add_simple_choice_to_scene(
                        current_scene.scene_id,
                        choice_text,
                        None,
                        None,
                        None,
                        None
                    )
            else:
                # Regular content line
                if current_scene:
                    scene_buffer.append(line)
        
        # Process the last scene
        if current_scene and scene_buffer:
            current_scene.content = '\n'.join(scene_buffer)
            
            # Set auto-transition if one was specified
            if auto_transition:
                current_scene.set_auto_transition(auto_transition, transition_text)
    
    def get_character_data(self) -> Dict[str, Dict[str, Any]]:
        """Get the parsed character data."""
        return self.characters
    
    def get_functions_code(self) -> str:
        """Get the parsed functions code."""
        return self.functions_code
    
    def get_metadata(self) -> Dict[str, str]:
        """Get the parsed metadata."""
        return self.metadata