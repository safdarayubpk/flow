#!/usr/bin/env python3
"""
Helper script for extending Task SQLModel with additional fields

This script demonstrates how to properly extend the Task model with
priority, tags, due_date, recurrence, and reminder fields while
maintaining backward compatibility.
"""

def main():
    print("This script demonstrates how to extend the Task SQLModel with new fields")
    print("while preserving existing fields and maintaining backward compatibility.")
    print("")
    print("Extension includes:")
    print("- priority: Optional[Literal['high', 'medium', 'low']]")
    print("- tags: List[str] stored as JSON")
    print("- due_date: Optional[datetime] with index")
    print("- recurrence_rule: Optional[str] for RRULE strings")
    print("- reminder_enabled: bool flag")

if __name__ == "__main__":
    main()
