# Text Adventure Engine Core Variables Reference

This document lists all the built-in variables, functions, and context available in the core engine for use in story files, templates, and conditional expressions.

## Game State Variables

### Basic Game State
- `game.day` - Current day number (starts at 1)
- `game.time_of_day` - Current time period ("morning", "afternoon", "evening", "night")
- `game.current_scene_id` - ID of the current scene
- `game.title` - Title of the current story

### Tracking Variables
- `game.visited_scenes` - Set of scene IDs that have been visited
- `game.completed_events` - Set of event IDs that have been completed

### Custom Variables
- Any variables set via `game.set_variable()` are accessible through the `var()` function

## Character Variables

### Player Character
- `player` - Direct access to the player character object
- `player.name` - Player character's name
- `player.is_player` - Always `True` for the player character
- `player.inventory` - List of items in the player's inventory
- `player.relationships` - Dictionary of relationship values with NPCs

### Player Stats
All available via `player.stats.*`, for example: `player.stats.health`
- Standard stats included in the core system:
  - `health` - Character health (0-100)
  - `energy` - Energy level (0-100)
  - `motivation` - Motivation level (0-100)
  - `weight` - Character's weight in kg
  - `height` - Character's height in cm
  - `fitness_level` - Fitness level (0-100)
  - `body_fat` - Body fat percentage (0-100)
  - `muscle_mass` - Muscle mass percentage (0-100)
  - `discipline` - Discipline level (0-100)
  - `stress` - Stress level (0-100)
  - `confidence` - Confidence level (0-100)
  - `days_since_exercise` - Days since last exercise
  - `sleep_hours` - Hours of sleep per night
  - `description` - Text description of the character

### Custom Character Attributes
- Any attributes set via `player.set_attribute()` or defined in character templates
- Examples from the fitness story:
  - `indulgence_streak` - Current streak of indulgent choices
  - `discipline_streak` - Current streak of disciplined choices
  - `satisfaction` - Satisfaction level (0-100)
  - `positivity` - Positivity level (0-100)

### NPC Access
- NPCs are accessible by their names with spaces removed, e.g., `CoachAlex`
- For NPCs with spaces in names, use `game.get_character("Coach Alex")`
- Access NPC stats and attributes the same way as player: `CoachAlex.stats.friendliness`

## Functions

### Game State Functions
- `var(name, default=None)` - Get value of a game variable, with optional default
- `has_completed(event_id)` - Check if an event has been completed (returns boolean)
- `game.get_character(name)` - Get a character by name (returns character object)
- `game.get_variable(name, default=None)` - Get a game variable (same as `var()`)

### Character Functions
- `player.get_attribute(name, default=None)` - Get a character attribute with default
- `player.has_stat(name)` - Check if a stat exists for this character
- `player.describe()` - Get a basic description of the character

### Description Functions
- `describe(character_name)` - Get a formatted description of a character

## Special Template Tags

### Variable Substitution
```
{{expression}}
```
Examples:
- `{{player.name}}`
- `{{player.stats.health}}`
- `{{game.day}}`
- `{{var('custom_variable', 0)}}`

### Formatted Variables
```
{{expression:format_spec}}
```
Examples:
- `{{player.stats.health:.0f}}` - No decimal places
- `{{player.stats.body_fat:.1f}}` - One decimal place
- `{{game.day:03d}}` - Padded with leading zeros

### Character Description Shorthand
```
{{describe:character_name}}
```
Example:
- `{{describe:Coach Alex}}`

### Conditional Blocks
```
{% if condition %}
  content
{% elif other_condition %}
  alternative content
{% else %}
  fallback content
{% endif %}
```

## Context Variables for Expressions and Conditions

When evaluating expressions (in `{{...}}`) or conditions (in `{% if ... %}`):

1. Direct access to:
   - `player` - The player character
   - `game` - The game state
   - All functions listed above

2. For `if` conditions in choices, additionally:
   - All player stats as direct variables (e.g., `health > 50` instead of `player.stats.health > 50`)

## Scene Variables

### In Scene Definitions
- `scene_id` - ID of the current scene
- `title` - Title of the current scene
- `content` - Main content text of the scene

### In Choice Definitions
- `text` - Text of the choice
- `action_id` - ID of the action to execute when chosen
- `next_scene` - ID of the scene to transition to
- `condition` - Condition for the choice to be available
- `next_story` - ID of the story to transition to