"""
Command-line interface for ticket classifier.
"""

import json
import sys
from pathlib import Path

from classifier import TicketClassifier


def load_sample_tickets() -> list[dict]:
    """Load sample tickets from JSON file."""
    sample_file = Path(__file__).parent / "sample_tickets.json"
    with open(sample_file, "r") as f:
        data = json.load(f)
    return data.get("tickets", data) if isinstance(data, dict) else data


def classify_ticket_interactive() -> None:
    """Interactive mode: prompt user for title and description."""
    print("\n" + "=" * 60)
    print("AI TICKET CLASSIFIER - Interactive Mode")
    print("=" * 60)

    classifier = TicketClassifier()

    title = input("\nEnter ticket title: ").strip()
    if not title:
        print("Error: Title cannot be empty")
        sys.exit(1)

    description = input("Enter ticket description: ").strip()
    if not description:
        print("Error: Description cannot be empty")
        sys.exit(1)

    result = classifier.classify(title, description)
    _print_result(result, title)


def classify_sample_tickets() -> None:
    """Demo mode: classify all sample tickets."""
    print("\n" + "=" * 60)
    print("AI TICKET CLASSIFIER - Sample Tickets Demo")
    print("=" * 60)

    classifier = TicketClassifier()

    try:
        # Try loading from sample_tickets.json
        tickets = load_sample_tickets()
    except Exception:
        # Fallback to hardcoded samples
        from sample_tickets import SAMPLE_TICKETS
        tickets = SAMPLE_TICKETS

    for i, ticket in enumerate(tickets, 1):
        title = ticket.get("title", "")
        description = ticket.get("description", "")
        ticket_id = ticket.get("id", f"SAMPLE-{i:03d}")

        if not title or not description:
            continue

        result = classifier.classify(title, description)
        print(f"\n[{i}/{len(tickets)}] {ticket_id}: {title}")
        _print_result(result, title)


def _print_result(result, title: str) -> None:
    """Pretty print classification result."""
    print(f"\n  Category:            {result.category.upper()}")
    print(f"  Priority:            {result.priority.upper()}")
    print(f"  Confidence:          {result.confidence:.0%}")
    print(f"  Recommended Action:  {result.recommended_action}")
    print("-" * 60)


def main() -> None:
    """Main CLI entry point."""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "demo":
            classify_sample_tickets()
            return
        elif mode == "interactive":
            classify_ticket_interactive()
            return
        elif mode in ["-h", "--help", "help"]:
            print_help()
            return
        else:
            print(f"Unknown mode: {mode}")
            print_help()
            sys.exit(1)

    # Default: demo mode
    classify_sample_tickets()


def print_help() -> None:
    """Print help message."""
    print("""
AI TICKET CLASSIFIER - Usage

Usage:
  python cli.py [MODE]

Modes:
  demo              Run demo with sample tickets (default)
  interactive       Classify a single ticket interactively
  help              Show this help message
  -h, --help        Show this help message

Examples:
  python cli.py
  python cli.py demo
  python cli.py interactive
    """)


if __name__ == "__main__":
    main()
