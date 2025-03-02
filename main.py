#!/usr/bin/env python3
# main.py - Main entry point for text adventure engine
import os
import sys
import argparse
from typing import Optional, Tuple, List

# Import engine components
from engine.engine import TextAdventureEngine
from frontends.text_interface import create_text_interface
from frontends.rich_interface import create_rich_interface


def setup_directories() -> Tuple[str, str]:
    """
    Set up the directories for stories and templates.
    
    Returns:
        Tuple[str, str]: (stories_dir, templates_dir)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stories_dir = os.path.join(base_dir, "stories")
    templates_dir = os.path.join(base_dir, "templates")
    
    # Ensure directories exist
    os.makedirs(stories_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)
    
    return stories_dir, templates_dir


def create_interface(interface_type: str):
    """
    Create the appropriate interface based on the type.
    
    Args:
        interface_type: Type of interface to create ('text', 'rich', 'gui')
        
    Returns:
        GameInterface: The created interface
    """
    if interface_type == "rich":
        try:
            return create_rich_interface()
        except ImportError:
            print("Rich library not installed. Falling back to text interface.")
            return create_text_interface()
    elif interface_type == "gui":
        print("GUI interface not yet implemented. Using text interface.")
        return create_text_interface()
    else:
        return create_text_interface()


def select_story(engine: TextAdventureEngine, interface) -> Optional[str]:
    """
    Select a story to play.
    
    Args:
        engine: Game engine
        interface: User interface
        
    Returns:
        str: Selected story ID or None if no story selected
    """
    stories = list(engine.story_paths.keys())
    if not stories:
        interface._display_message("No stories found.")
        return None
    
    # Display available stories
    interface._display_message("Available stories:")
    
    # Use the interface to select from the list
    story_index = interface.select_from_list(stories, "Please select a story:")
    if story_index < 0:
        interface._display_message("No story selected.")
        return None
    
    return stories[story_index]


def get_player_name(interface) -> str:
    """
    Get the player character name.
    
    Args:
        interface: User interface
        
    Returns:
        str: Player name (defaults to "Player" if none provided)
    """
    player_name = interface._get_user_input("Enter your character name (leave blank for default):")
    return player_name.strip() or "Player"


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Text Adventure Game Engine")
    parser.add_argument("story_file", nargs="?", help="Path to the story file (.tadv)")
    parser.add_argument("--player", "-p", help="Player character name")
    parser.add_argument("--list-stories", "-l", action="store_true", help="List available stories")
    parser.add_argument("--interface", "-i", choices=["text", "rich", "gui"], default="text", 
                      help="Interface to use (default: text)")
    
    args = parser.parse_args()
    
    # Set up directories
    stories_dir, templates_dir = setup_directories()
    
    # Create and initialize the engine
    engine = TextAdventureEngine()
    engine.set_directories(stories_dir, templates_dir)
    
    # Create the appropriate interface
    interface = create_interface(args.interface)
    interface.initialize(engine)
    
    # List available stories if requested and exit
    if args.list_stories:
        stories = list(engine.story_paths.keys())
        if stories:
            for i, story in enumerate(stories, 1):
                interface._display_message(f"{i}. {story}")
        else:
            interface._display_message("No stories found.")
        return
    
    # Determine the story to load
    story_file = args.story_file
    if not story_file:
        story_file = select_story(engine, interface)
        if not story_file:
            return  # Exit if no story selected
    
    # Get player name
    player_name = args.player
    if not player_name:
        player_name = get_player_name(interface)
    
    # Load the story file
    interface._display_message(f"Loading story: {story_file}")
    try:
        if not engine.load_story(story_file):
            interface._display_message("Failed to load story.")
            return
    except Exception as e:
        interface._display_message(f"Error loading story: {e}")
        return
    
    # Initialize game with player name
    try:
        if not engine.initialize_game(player_name=player_name):
            interface._display_message("Failed to initialize game.")
            return
    except Exception as e:
        interface._display_message(f"Error initializing game: {e}")
        return
    
    # Start the game loop
    try:
        interface.game_loop()
    except KeyboardInterrupt:
        interface._display_message("\nGame interrupted. Exiting...")
    except Exception as e:
        interface._display_message(f"Error during game: {e}")


if __name__ == "__main__":
    main()