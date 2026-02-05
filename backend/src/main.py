#!/usr/bin/env python3
"""
Entry point for the Console Todo App.

This module initializes the application components and starts the CLI interface.
"""

from task_manager import TaskManager
from cli_interface import CLIInterface


def main():
    """
    Main function to run the Console Todo App.

    Initializes the task manager and CLI interface, then starts the application.
    """
    print("Initializing Console Todo App...")

    # Initialize the task manager
    task_manager = TaskManager()

    # Initialize the CLI interface with the task manager
    cli_interface = CLIInterface(task_manager)

    # Start the application
    try:
        cli_interface.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye! Thanks for using the Console Todo App.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Application terminating.")


if __name__ == "__main__":
    main()
