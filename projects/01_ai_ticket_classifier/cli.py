"""
Command-line interface for the AI Ticket Classifier.

Provides demo and interactive modes for classifying SRE tickets.

Example usage:
    python cli.py demo              # Run with sample tickets
    python cli.py interactive       # Classify single ticket interactively
    python cli.py help              # Show help message
"""

import json
import sys
from pathlib import Path

from classifier import TicketClassifier


def load_sample_tickets() -> list:
    """Load sample tickets from JSON file.

    Returns:
        List of ticket dictionaries with id, title, and description

    Raises:
        FileNotFoundError: If sample_tickets.json not found
        json.JSONDecodeError: If JSON is malformed
    """
    sample_file = Path(__file__).parent / "sample_tickets.json"
    with open(sample_file, "r") as f:
        data = json.load(f)

    # Handle both dict with "tickets" key and plain list
    if isinstance(data, dict):
        return data.get("tickets", [])
    return data


def classify_sample_tickets() -> None:
    """Run classifier in demo mode with sample tickets."""
    print("\n" + "=" * 70)
    print("AI TICKET CLASSIFIER - Sample Tickets Demo")
    print("=" * 70)

    classifier = TicketClassifier()

    try:
        tickets = load_sample_tickets()
    except Exception as err:
        print(f"Error loading sample tickets: {err}")
        sys.exit(1)

    if not tickets:
        print("No sample tickets found.")
        sys.exit(1)

    for i, ticket in enumerate(tickets, 1):
        title = ticket.get("title", "")
        description = ticket.get("description", "")
        ticket_id = ticket.get("id", f"SAMPLE-{i:03d}")

        if not title or not description:
            continue

        result = classifier.classify(title, description)
        _print_result(i, ticket_id, title, result)


def classify_ticket_interactive() -> None:
    """Run classifier in interactive mode for single ticket."""
    print("\n" + "=" * 70)
    print("AI TICKET CLASSIFIER - Interactive Mode")
    print("=" * 70)

    classifier = TicketClassifier()

    # Get title from user
    title = input("\nEnter ticket title: ").strip()
    if not title:
        print("Error: Title cannot be empty")
        sys.exit(1)

    # Get description from user
    description = input("Enter ticket description: ").strip()
    if not description:
        print("Error: Description cannot be empty")
        sys.exit(1)

    # Classify the ticket
    result = classifier.classify(title, description)

    # Display result
    print("\n" + "-" * 70)
    print(f"Category:            {result.category.upper()}")
    print(f"Priority:            {result.priority.upper()}")
    print(f"Confidence:          {result.confidence:.0%}")
    print(f"Recommended Action:  {result.recommended_action}")
    print("=" * 70 + "\n")


def _print_result(index: int, ticket_id: str, title: str, result) -> None:
    """Pretty print a classification result.

    Args:
        index: Item number in the list
        ticket_id: The ticket identifier
        title: The ticket title
        result: ClassificationResult object
    """
    print(f"\n[{index}] {ticket_id}: {title}")
    print(f"  Category:           {result.category.upper()}")
    print(f"  Priority:           {result.priority.upper()}")
    print(f"  Confidence:         {result.confidence:.0%}")
    print(f"  Recommended Action: {result.recommended_action}")
    print("-" * 70)


def print_help() -> None:
    """Print help message and usage information."""
    help_text = """
AI TICKET CLASSIFIER - Command Line Interface

Usage:
  python cli.py [MODE]

Modes:
  demo              Run demo with 10 sample SRE tickets (default)
  interactive       Classify a single ticket interactively
  help              Show this help message
  -h, --help        Show this help message

Examples:
  python cli.py
  python cli.py demo
  python cli.py interactive
  python cli.py help

Description:
  This tool classifies SRE and infrastructure tickets into categories
  (incident, deployment, config_change, access_request, investigation)
  and assigns priority levels (critical, high, medium, low).

  It uses rule-based keyword matching and requires no external APIs.

Categories:
  - incident:        Production issues, system outages, performance problems
  - deployment:      Release planning, version upgrades, rollouts
  - config_change:   Monitoring updates, threshold changes, policy updates
  - access_request:  Permissions, credentials, SSH keys
  - investigation:   Root cause analysis, debugging, security review

Priority Levels:
  - critical:        P0, production-down scenarios
  - high:            P1, significant impact
  - medium:          P2, moderate impact
  - low:             P3, minor or non-urgent
    """
    print(help_text)


def main() -> None:
    """Main entry point for CLI application.

    Parses command-line arguments and routes to appropriate function.
    """
    # Check for command-line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == "demo":
            classify_sample_tickets()
            return

        if mode == "interactive":
            classify_ticket_interactive()
            return

        if mode in ["-h", "--help", "help"]:
            print_help()
            return

        # Unknown mode
        print(f"Error: Unknown mode '{mode}'")
        print_help()
        sys.exit(1)

    # Default: run demo mode
    classify_sample_tickets()


if __name__ == "__main__":
    main()
