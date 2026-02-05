"""
Utility functions for the Console Todo App.

This module contains helper functions for input validation,
formatting, and other common operations.
"""

from typing import Optional


def get_positive_int_input(prompt: str) -> int:
    """
    Get a positive integer input from the user.

    Args:
        prompt (str): The prompt to display to the user

    Returns:
        int: A positive integer entered by the user

    Raises:
        ValueError: If the input is not a positive integer
    """
    while True:
        try:
            value = input(prompt)
            num = int(value)
            if num <= 0:
                print("Please enter a positive number.")
                continue
            return num
        except ValueError:
            print("Please enter a valid number.")


def get_non_empty_string_input(prompt: str) -> str:
    """
    Get a non-empty string input from the user.

    Args:
        prompt (str): The prompt to display to the user

    Returns:
        str: A non-empty string entered by the user
    """
    while True:
        value = input(prompt).strip()
        if not value:
            print("Input cannot be empty. Please try again.")
            continue
        return value


def format_task_list(tasks: list) -> str:
    """
    Format a list of tasks for display.

    Args:
        tasks (list): A list of task objects

    Returns:
        str: A formatted string representation of the tasks
    """
    if not tasks:
        return "No tasks found."

    header = "ID | Status | Title | Description"
    separator = "-" * len(header)

    task_lines = [header, separator]
    for task in tasks:
        task_str = str(task)
        # Extract description to add to the formatted line
        desc = getattr(task, 'description', '') or ''
        formatted_line = f"{task.id:2} | {'[x]' if task.completed else '[ ]'} | {task.title.strip()} | {desc}"
        task_lines.append(formatted_line)

    return "\n".join(task_lines)


def safe_int_parse(value: str) -> Optional[int]:
    """
    Safely parse a string to an integer.

    Args:
        value (str): The string to parse

    Returns:
        Optional[int]: The parsed integer or None if parsing fails
    """
    try:
        return int(value)
    except ValueError:
        return None


def confirm_action(prompt: str) -> bool:
    """
    Ask the user to confirm an action.

    Args:
        prompt (str): The confirmation prompt

    Returns:
        bool: True if user confirms, False otherwise
    """
    response = input(f"{prompt} (y/N): ").strip().lower()
    return response in ['y', 'yes']