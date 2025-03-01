# Text Adventure File Format Specification

## Introduction
This document defines the format for `.tadv` (Text Adventure) and `.tscene` (Text Adventure Scene) files used by the Text Adventure Engine. These files use a simple text-based format with sections, directives, and special syntax for defining interactive stories.

## File Types

### .tadv Files
These are complete story files that include metadata, character definitions, functions, and scenes. They define a full interactive story experience.

### .tscene Files
These are modular scene files that focus on scene definitions and their associated functions. They can be imported into .tadv files to support modular story development.

## Common Syntax Elements

### Comments
Lines starting with `#` are treated as comments and ignored during parsing:
```
# This is a comment
```

### Section Markers
Sections are delimited by `===` markers:
```
=== SECTION_NAME ===
```

### Import Directives
Import directives start with `@import` and specify a file path to import:
```
@import filename.tscene
```

### Choice Lines
Choices begin with an asterisk `*`:
```
* This is a choice -> action_id goto:scene_id
```

### Scene Headers
Scene definitions start with `---` followed by an ID and title:
```
--- scene_id: Scene Title ---
```

## .tadv File Structure

A .tadv file consists of several sections, each with a specific purpose:

### METADATA Section
Defines general information about the story:
```
=== METADATA ===
Title: Story Title
Start: starting_scene_id
Author: Author Name
Version: 1.0
```

### CHARACTERS Section
Defines characters in the story, with optional template imports:
```
=== CHARACTERS ===
- Player@player.tchar
    health: 100.0
    fitness_level: 30.0

- NPC Name
    description: A helpful guide
    friendliness: 80.0
```

Character template imports use the `@` symbol:
```
- Character Name@template_file.tchar
    # Override attributes
    strength: 75.0
```

### FUNCTIONS Section
Contains Python code that defines functions for the story:
```
=== FUNCTIONS ===
def function_name(game):
    """Function documentation."""
    state = game
    player = state.player
    
    # Function logic here
    player.update_stats(health=player.stats.health + 10)
    
    return "Function result text."

# Register functions
register_action("action_id", function_name)
```

### SCENE Section
Defines story scenes with text content and choices:
```
=== SCENE ===
--- scene_id: Scene Title ---
This is the main text content for the scene.
It can span multiple lines and may include template tags.

{% if player.stats.health < 50 %}
You're feeling quite weak.
{% else %}
You feel strong and healthy.
{% endif %}

* Make this choice -> action_id goto:next_scene
* Another choice -> goto:different_scene
* Conditional choice -> goto:scene_a if player.stats.health > 50 else goto:scene_b
```

## .tscene File Structure

A .tscene file has a simplified structure focused on scenes and related functions:

```
# scene_file.tscene - Scene-specific content

=== FUNCTIONS ===
# Scene-specific functions
def scene_function(game):
    # Function logic
    return "Result text"

register_action("scene_action", scene_function)

=== SCENE ===
--- scene_id_1: First Scene Title ---
Scene content here.

* First choice -> action_id goto:next_scene
* Second choice -> goto:another_scene

--- scene_id_2: Second Scene Title ---
Another scene's content.

* A choice -> action_id goto:next_scene
```

## Template Tags

The engine supports powerful template tags for dynamic content:

### Variable Substitution
```
{{variable_name}}
{{player.stats.health}}
{{game.day}}
```

With formatting:
```
{{variable_name:format_spec}}
{{player.stats.health:.1f}}
```

### Conditional Blocks
```
{% if condition %}
  Content shown when condition is true
{% elif other_condition %}
  Content shown when other_condition is true
{% else %}
  Content shown when no conditions are true
{% endif %}
```

## Choice Syntax

Choices use a special syntax for defining player options and their effects:

```
* Choice text -> [action_id] [goto:scene_id] [if condition]
```

Components:
- `*` - Indicates a choice line
- `Choice text` - Text shown to the player
- `->` - Separator between choice text and actions
- `action_id` - ID of an action to execute (optional)
- `goto:scene_id` - Scene to transition to (optional)
- `if condition` - Condition for choice availability (optional)

Examples:
```
* Open the door -> goto:hallway
* Drink the potion -> drink_potion goto:same_room
* Attack with sword -> attack if player.stats.strength > 50
* Run away -> run_away goto:forest if player.stats.health < 30
* Complex decision -> goto:good_path if player.stats.morality > 70 else goto:evil_path
```

## Best Practices

1. **Organization**:
   - Keep related scenes in dedicated .tscene files
   - Use consistent naming for files, scenes, and actions
   - Group related functions together

2. **Content Structure**:
   - Start each scene with context-setting descriptions
   - Use conditional blocks to personalize content
   - Provide meaningful choice text that hints at outcomes

3. **Technical**:
   - Register all action functions
   - Document functions with docstrings
   - Handle edge cases in conditional logic

4. **Scene Flow**:
   - Ensure every scene has at least one choice or is an ending
   - Use conditions to control access to choices
   - Consider providing "back" options where appropriate