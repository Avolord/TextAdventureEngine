import re
from typing import List, Dict, Any, Optional, NamedTuple, Tuple

class ChoiceData:
    """Data extracted from a choice line in a template."""
    def __init__(self, text="", action_id=None, next_scene=None, next_story=None):
        self.text = text
        self.action_id = action_id
        self.next_scene = next_scene
        self.next_story = next_story

class TemplateResult:
    """Result of template processing containing different types of processed content."""
    def __init__(self, text="", choices=None, auto_transition=None, transition_text=None):
        self.text = text  # The main text content
        self.choices = choices or []  # Extracted choices
        self.auto_transition = auto_transition  # Next scene ID for auto-transition
        self.transition_text = transition_text  # Text for auto-transition

class TemplateProcessor:
    """
    A modular template processor that handles text templates with variables,
    conditionals (if/elif/else), and choice extraction.
    """
    def process(self, text: str, context: Dict[str, Any]) -> TemplateResult:
        """
        Process template tags in text and extract structured information.
        
        Args:
            text: Text to process
            context: Context dictionary with variables for evaluation
            
        Returns:
            TemplateResult: Processed text and extracted info
        """
        if not text:
            return TemplateResult()
        
        # Reset auto-transition info
        self.auto_transition = None
        self.transition_text = None
        
        # Process conditional blocks first (important for nested conditionals)
        processed_text = self._process_conditionals(text, context)
        
        # Process variable substitutions
        processed_text = self._process_variables(processed_text, context)
        
        # Extract choices
        choices = self._extract_choices(processed_text)
        
        # Filter out choice lines from the display text
        display_text = self._filter_choice_lines(processed_text)
        
        # Create result with auto-transition info
        auto_transition, transition_text = self.get_auto_transition()
        return TemplateResult(display_text, choices, auto_transition, transition_text)
    
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """
        Process template tags in text without extracting choices.
        Useful for processing choice text or other content.
        
        Args:
            text: Text to process
            context: Context dictionary with variables for evaluation
            
        Returns:
            str: Processed text
        """
        if not text:
            return ""
        
        # Process conditional blocks
        text = self._process_conditionals(text, context)
        
        # Process variable substitutions
        text = self._process_variables(text, context)
        
        return text
    
    def _filter_choice_lines(self, text: str) -> str:
        """
        Filter out lines that represent choices.
        
        Args:
            text: Text to filter
            
        Returns:
            str: Filtered text
        """
        filtered_lines = []
        for line in text.split('\n'):
            # Skip choice lines (those starting with '*')
            if line.strip().startswith('*'):
                continue
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _extract_choices(self, text: str) -> List[ChoiceData]:
        """
        Extract choices from processed text.
        
        Args:
            text: Processed text potentially containing choice lines
            
        Returns:
            List of ChoiceData objects
        """
        choices = []
        
        # Extract lines that start with '*' (choices)
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('*'):
                choice_text = line[1:].strip()
                
                # Create choice data with defaults
                choice_data = ChoiceData(choice_text)
                
                # Check if there's an action/goto
                if '->' in choice_text:
                    text, action_data = choice_text.split('->', 1)
                    choice_data.text = text.strip()
                    action_data = action_data.strip()
                    
                    # Extract action_id if present (text before any keywords)
                    action_parts = action_data.split()
                    action_id_parts = []
                    
                    for part in action_parts:
                        if part.startswith(('goto:', 'story:')):
                            break
                        action_id_parts.append(part)
                    
                    if action_id_parts:
                        choice_data.action_id = ' '.join(action_id_parts)
                    
                    # Check for goto
                    goto_match = re.search(r'goto:(\w+)', action_data)
                    if goto_match:
                        choice_data.next_scene = goto_match.group(1)
                    
                    # Check for story transition
                    story_match = re.search(r'story:(\w+)(?::(\w+))?', action_data)
                    if story_match:
                        choice_data.next_story = story_match.group(1)
                        if story_match.group(2):  # Optional scene in new story
                            choice_data.next_scene = story_match.group(2)
                
                choices.append(choice_data)
        
        return choices
    
    def _process_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Process variable substitutions with format specifiers."""
        # Pattern matches {{expression:format_spec}}
        pattern = r'\{\{(.*?)(?::([^}]+))?\}\}'
        
        def replace_var(match):
            var_expr = match.group(1).strip()
            format_spec = match.group(2)  # This will be None if no format was specified
            
            try:
                # Evaluate the expression in context
                result = eval(var_expr, {"__builtins__": {}}, context)
                
                # Apply format specifier if provided
                if format_spec:
                    try:
                        # Only apply formatting if it makes sense
                        if isinstance(result, (int, float)):
                            format_str = f"{{:{format_spec}}}"
                            return format_str.format(result)
                        else:
                            # For non-numeric values, just convert to string
                            return str(result)
                    except ValueError as e:
                        # If formatting fails, just return as string
                        print(f"Format error ({format_spec}) for {result}: {e}")
                        return str(result)
                
                return str(result)
            except Exception as e:
                print(f"Error evaluating expression '{var_expr}': {e}")
                return f"{{Error: {e}}}"
        
        return re.sub(pattern, replace_var, text)
    
    def _process_conditionals(self, text: str, context: Dict[str, Any]) -> str:
        """Process conditional blocks with if/elif/else support and scene transitions."""
        # Find all complete if-elif-else-endif blocks
        pattern = r'\{%\s*if\s+(.+?)\s*%\}(.*?)(?:\{%\s*elif\s+.*?%\}.*?)*(?:\{%\s*else\s*%\}.*?)?\{%\s*endif\s*%\}'
        
        # Process the text to find all conditional blocks
        while True:
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                break
                
            full_block = match.group(0)
            result = self._evaluate_conditional_block(full_block, context)
            
            # Replace the entire conditional block with its result
            text = text.replace(full_block, result)
        
        # Extract auto-transition directives
        auto_transition = None
        transition_text = None
        
        # Look for @goto directive anywhere in the text
        goto_pattern = r'@goto:(\w+)(?:\s+(.+?))?$'
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('@goto:'):
                match = re.search(goto_pattern, line)
                if match:
                    auto_transition = match.group(1)
                    transition_text = match.group(2) if match.group(2) else None
                    # Remove the directive line from text
                    text = text.replace(line, '', 1)
        
        # Store auto-transition info in the template processor for later retrieval
        self.auto_transition = auto_transition
        self.transition_text = transition_text
                
        return text
    
    def _evaluate_conditional_block(self, block: str, context: Dict[str, Any]) -> str:
        """
        Evaluate a complete if-elif-else-endif conditional block.
        
        Args:
            block: Complete conditional block text
            context: Context dictionary with variables for evaluation
            
        Returns:
            str: Content of the matched condition or empty string
        """
        # Split the block into segments (if, elif(s), else)
        segments = []
        
        # Extract the if condition and content
        if_match = re.search(r'\{%\s*if\s+(.+?)\s*%\}(.*?)(?:\{%|$)', block, re.DOTALL)
        if if_match:
            segments.append(('if', if_match.group(1), if_match.group(2)))
        
        # Extract all elif conditions and content
        pos = 0
        while True:
            elif_match = re.search(r'\{%\s*elif\s+(.+?)\s*%\}(.*?)(?:\{%|$)', block[pos:], re.DOTALL)
            if not elif_match:
                break
                
            segments.append(('elif', elif_match.group(1), elif_match.group(2)))
            pos += elif_match.end()
        
        # Extract the else content if present
        else_match = re.search(r'\{%\s*else\s*%\}(.*?)(?:\{%|$)', block, re.DOTALL)
        if else_match:
            segments.append(('else', None, else_match.group(1)))
        
        # Evaluate each segment in order
        for segment_type, condition, content in segments:
            if segment_type == 'else':
                return content  # No condition to evaluate for else
                
            # Make condition null-safe
            safe_condition = self._make_condition_null_safe(condition)
            
            try:
                # Evaluate the condition
                if eval(safe_condition, {"__builtins__": {}}, context):
                    return content
            except Exception as e:
                print(f"Error evaluating condition '{condition}': {e}")
                return f"{{Error in condition: {e}}}"
        
        # If no conditions were true and no else block, return empty string
        return ""
        
    def _make_condition_null_safe(self, condition: str) -> str:
        """
        Make a condition null-safe by adding existence checks.
        This helps prevent errors when comparing to None values.
        
        Args:
            condition: Original condition string
            
        Returns:
            Modified condition string
        """
        # Handle common attribute access patterns to make them null-safe
        patterns = [
            # player.stats.X > Y becomes (player.stats.X or 0) > Y
            (r'(player\.stats\.\w+)\s*(==|!=|>|<|>=|<=)\s*(\d+(?:\.\d+)?)',
             r'(\1 or 0) \2 \3'),
            
            # X > player.stats.Y becomes X > (player.stats.Y or 0)
            (r'(\d+(?:\.\d+)?)\s*(==|!=|>|<|>=|<=)\s*(player\.stats\.\w+)',
             r'\1 \2 (\3 or 0)'),
        ]
        
        # Apply each pattern
        for pattern, replacement in patterns:
            condition = re.sub(pattern, replacement, condition)
        
        return condition
    
    def get_auto_transition(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get auto-transition information extracted during processing.
        
        Returns:
            Tuple of (next_scene_id, transition_text)
        """
        return getattr(self, 'auto_transition', None), getattr(self, 'transition_text', None)