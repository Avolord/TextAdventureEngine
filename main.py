#!/usr/bin/env python3
# main.py - Main entry point with interface support
import os
import sys
import argparse

# Import from the engine package
from engine.engine import TextAdventureEngine
from engine.interface import InterfaceManager
from frontends.text_interface import create_text_interface
from frontends.rich_interface import create_rich_interface

# Import other frontends as they become available
# from text_adventure.frontends.gui_interface import create_gui_interface


def main():
    """Run the text adventure game."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Text Adventure Game Engine")
    parser.add_argument("story_file", nargs="?", help="Path to the story file (.tadv)")
    parser.add_argument("--player", "-p", help="Player character name")
    parser.add_argument("--list-stories", "-l", action="store_true", help="List available stories")
    parser.add_argument("--interface", "-i", choices=["text", "gui", "rich"], default="text", 
                      help="Interface to use (default: text)")
    
    args = parser.parse_args()
    
    # Set up directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stories_dir = os.path.join(base_dir, "stories")
    templates_dir = os.path.join(base_dir, "templates")
    
    # Set up engine
    engine = TextAdventureEngine()
    engine.set_directories(stories_dir, templates_dir)
    
    # Set up interface manager
    interface_manager = InterfaceManager()
    
    # Create interface based on argument
    if args.interface == "text":
        interface = create_text_interface()
    elif args.interface == "rich":
        interface = create_rich_interface()
    elif args.interface == "gui":
        # When GUI is implemented
        # interface = create_gui_interface()
        print("GUI interface not yet implemented. Using text interface.")
        interface = create_text_interface()
    else:
        print(f"Unknown interface: {args.interface}. Using text interface.")
        interface = create_text_interface()
    
    # Set interface
    interface_manager.set_interface(interface)
    interface.initialize(engine)
    
    # List available stories if requested
    if args.list_stories:
        stories = list(engine.story_paths.keys())
        if stories:
            interface.display_message("Available stories:")
            for i, story in enumerate(stories, 1):
                interface.display_message(f"{i}. {story}")
        else:
            interface.display_message("No stories found.")
        return
    
    # Get story file
    story_file = args.story_file
    if not story_file:
        # If no story file provided, prompt the user
        stories = list(engine.story_paths.keys())
        if stories:
            story_index = interface.select_from_list(stories, "Available stories:")
            if story_index >= 0:
                story_file = stories[story_index]
            else:
                interface.display_message("No story selected. Exiting.")
                return
        else:
            interface.display_message("No stories found.")
            return
    
    # Get player name
    player_name = args.player
    if not player_name:
        player_name = interface.get_user_input("Enter your character name (leave blank for default):")
        if not player_name:
            player_name = "Player"  # Default name
    
    # Load the story file
    interface.display_message(f"\nLoading story: {story_file}")
    if not engine.load_story(story_file):
        interface.display_message("Failed to load story.")
        return
    
    # Initialize game with player name
    if not engine.initialize_game(player_name=player_name):
        interface.display_message("Failed to initialize game.")
        return
    
    # Start the game loop
    interface.game_loop(engine)


if __name__ == "__main__":
    main()