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

#### Custom Descriptor Functions
You can define and register custom descriptor functions:
```
=== FUNCTIONS ===
def athletic_descriptor(stats):
    """Custom descriptor for athletic characters."""
    if stats.fitness_level and stats.fitness_level > 70:
        return "athletic with well-defined muscles"
    elif stats.muscle_mass and stats.muscle_mass > 60:
        return "muscular and fit"
    else:
        return "athletic"

# Register the custom descriptor
register_body_descriptor("athletic", athletic_descriptor)

# Function to change descriptors
def become_more_detailed(game):
    """Set characters to use more detailed descriptions."""
    set_character_descriptor(game.player.name, "body", "fitness")
    set_character_descriptor(game.player.name, "energy", "detailed")
    return "Your descriptive style has changed to be more detailed."

register_action("more_detail", become_more_detailed)
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
* Change description style -> change_body_descriptor
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

### Character Description Tags
Basic character description:
```
{{describe:character_name}}
```

Enhanced character description with specific descriptor types:
```
{{describe:character_name:body_type:energy_type}}
```

Examples:
```
{{describe:player:fitness:detailed}}
{{describe:Coach Alex:athletic:simple}}
```

Get just the body or energy description:
```
{{get_body_desc:character_name:descriptor_type}}
{{get_energy_desc:character_name}}
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
* Change description style -> change_body_descriptor
* Undo last action -> undo
```

## Built-in Actions

The engine includes several built-in actions:

- `change_body_descriptor` - Change the body descriptor style for the player
- `change_energy_descriptor` - Change the energy descriptor style for the player
- `undo` - Undo the last action

## Save System Commands

The following commands can be used during gameplay:

- `save [name]` - Save the current game state
- `load [name]` - Load a saved game
- `saves` or `list` - List all saved games
- `delete [name]` - Delete a saved game
- `undo` - Undo the last action
- `help` - Show available commands

## Auto-Transition Directives

The engine now supports automatic scene transitions in several ways:

### 1. Scene Definition Auto-Transitions

Add an `@goto` directive at the end of a scene to create an automatic transition that occurs when the user presses Enter:

```
--- intro_scene: Introduction ---
Welcome to the adventure.

This is a scene without choices that automatically continues to the next scene.

@goto:next_scene The story continues...
```

The format is `@goto:scene_id [optional transition text]`. The transition text (if provided) will be shown briefly before the new scene.

### 2. Conditional Auto-Transitions

Auto-transitions can be placed inside conditional blocks:

```
{% if player.stats.health < 20 %}
You feel extremely weak...

@goto:hospital You pass out and wake up in the hospital.
{% else %}
You manage to keep going despite your wounds.
{% endif %}
```

### 3. Programmatic Scene Transitions

Story authors can use the built-in `goto_scene` function in their action handlers:

```python
def after_conversation(game):
    """Handle post-conversation logic."""
    # Update player state
    game.player.update_stats(stress=game.player.stats.stress - 10)
    
    # Determine which scene to go to next
    if game.player.stats.stress < 30:
        goto_scene("relaxed_outcome")
    else:
        goto_scene("stressed_outcome")
    
    return "The conversation ends."

register_action("end_conversation", after_conversation)
```

### 4. Using the Built-in "goto" Action

A built-in "goto" action is available for use in choices:

```
* Leave the room -> goto goto:hallway
```

## How Auto-Transitions Work

1. **Scenes without choices**: If a scene has an auto-transition but no choices, the user is prompted to press Enter to continue (or can enter a command).

2. **Template directives**: The `@goto:scene_id` syntax can be used in scene content or conditional blocks.

3. **Programmatic transitions**: Functions can call `goto_scene(scene_id)` to trigger transitions.

4. **Transition text**: Optional text can be shown during the transition to provide context or narration.

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

5. **Descriptors**:
   - Define custom descriptors for important characters
   - Use appropriate descriptor types for different scenes
   - Consider offering choices that change descriptor styles

6. **Save System**:
   - Provide opportunities for players to save at important points
   - Use undo functionality for reversible decisions
   - Implement autosave at major story branches

7. **Auto Transitions**:
   - Use auto-transitions for linear narrative sections where no player choice is needed.
   - Provide meaningful transition text to create smooth narrative flow.
   - Use conditional auto-transitions to create branching paths based on player state.
   - Consider adding a choice for "Continue..." even in auto-transition scenes to make progression more explicit.