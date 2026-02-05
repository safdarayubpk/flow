"""
Command-Line Interface for the Console Todo App.

This module handles all user interactions through the console,
displaying menus and processing user input.
"""

import sys
from typing import Optional
from task_manager import TaskManager
from utils import get_positive_int_input, get_non_empty_string_input, format_task_list, safe_int_parse, confirm_action


class CLIInterface:
    """
    Handles the command-line interface for the todo application.

    Provides methods for displaying menus, getting user input,
    and executing user commands.
    """

    def __init__(self, task_manager: TaskManager):
        """
        Initialize the CLI interface.

        Args:
            task_manager (TaskManager): The task manager instance to use
        """
        self.task_manager = task_manager

    def display_menu(self) -> None:
        """Display the main menu options to the user."""
        print("\n" + "="*50)
        print("           CONSOLE TODO APPLICATION")
        print("="*50)
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Complete/Incomplete")
        print("6. Quit")
        print("-"*50)

    def get_user_choice(self) -> int:
        """
        Get the user's menu choice.

        Returns:
            int: The selected menu option (1-6)
        """
        while True:
            try:
                choice = get_positive_int_input("Enter your choice (1-6): ")
                if 1 <= choice <= 6:
                    return choice
                else:
                    print("Please enter a number between 1 and 6.")
            except ValueError:
                print("Please enter a valid number.")

    def handle_add_task(self) -> None:
        """Handle the Add Task operation."""
        print("\n--- ADD TASK ---")

        try:
            title = get_non_empty_string_input("Enter task title: ")

            description_input = input("Enter task description (optional, press Enter to skip): ").strip()
            description = description_input if description_input else None

            task = self.task_manager.create_task(title, description)
            print(f"\n✅ Task added successfully! Assigned ID: {task.id}")

        except ValueError as e:
            print(f"\n❌ Error: {e}")

    def handle_view_tasks(self) -> None:
        """Handle the View Tasks operation."""
        print("\n--- VIEW TASKS ---")

        tasks = self.task_manager.list_tasks()

        if not tasks:
            print("\nNo tasks found.")
        else:
            print("\nCurrent tasks:")
            print(format_task_list(tasks))

    def handle_update_task(self) -> None:
        """Handle the Update Task operation."""
        print("\n--- UPDATE TASK ---")

        if not self.task_manager.list_tasks():
            print("\nNo tasks available to update.")
            return

        try:
            task_id = get_positive_int_input("Enter the task ID to update: ")

            if not self.task_manager.has_task(task_id):
                print(f"\n❌ Error: Task with ID {task_id} does not exist.")
                return

            print(f"Updating task {task_id}: {self.task_manager.get_task(task_id)}")

            title_input = input("Enter new title (leave blank to keep current): ").strip()
            title = title_input if title_input else None

            desc_input = input("Enter new description (leave blank to keep current): ").strip()
            description = desc_input if desc_input else None

            # If both inputs are empty, nothing to update
            if title is None and description is None:
                print("\nNo changes provided. Task remains unchanged.")
                return

            task = self.task_manager.update_task(task_id, title, description)
            print(f"\n✅ Task {task_id} updated successfully!")

        except ValueError as e:
            print(f"\n❌ Error: {e}")

    def handle_delete_task(self) -> None:
        """Handle the Delete Task operation."""
        print("\n--- DELETE TASK ---")

        if not self.task_manager.list_tasks():
            print("\nNo tasks available to delete.")
            return

        try:
            task_id = get_positive_int_input("Enter the task ID to delete: ")

            if not self.task_manager.has_task(task_id):
                print(f"\n❌ Error: Task with ID {task_id} does not exist.")
                return

            task = self.task_manager.get_task(task_id)
            print(f"You are about to delete: {task}")

            if confirm_action("Are you sure you want to delete this task?"):
                self.task_manager.delete_task(task_id)
                print(f"\n✅ Task {task_id} deleted successfully!")
            else:
                print("\n❌ Task deletion cancelled.")

        except ValueError as e:
            print(f"\n❌ Error: {e}")

    def handle_toggle_completion(self) -> None:
        """Handle the Mark Complete/Incomplete operation."""
        print("\n--- MARK COMPLETE/INCOMPLETE ---")

        if not self.task_manager.list_tasks():
            print("\nNo tasks available to update.")
            return

        try:
            task_id = get_positive_int_input("Enter the task ID to toggle: ")

            if not self.task_manager.has_task(task_id):
                print(f"\n❌ Error: Task with ID {task_id} does not exist.")
                return

            task = self.task_manager.get_task(task_id)
            new_status = not task.completed
            self.task_manager.toggle_task_completion(task_id)

            status_text = "completed" if new_status else "incomplete"
            print(f"\n✅ Task {task_id} marked as {status_text}!")

        except ValueError as e:
            print(f"\n❌ Error: {e}")

    def handle_quit(self) -> None:
        """Handle the Quit operation."""
        print("\n👋 Goodbye! Thanks for using the Console Todo App.")
        sys.exit(0)

    def run(self) -> None:
        """
        Run the main application loop.

        Continuously display the menu and handle user choices until quit.
        """
        print("Welcome to the Console Todo App!")

        while True:
            try:
                self.display_menu()
                choice = self.get_user_choice()

                if choice == 1:
                    self.handle_add_task()
                elif choice == 2:
                    self.handle_view_tasks()
                elif choice == 3:
                    self.handle_update_task()
                elif choice == 4:
                    self.handle_delete_task()
                elif choice == 5:
                    self.handle_toggle_completion()
                elif choice == 6:
                    self.handle_quit()

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using the Console Todo App.")
                sys.exit(0)
            except Exception as e:
                print(f"\n❌ An unexpected error occurred: {e}")
                print("Please try again.")