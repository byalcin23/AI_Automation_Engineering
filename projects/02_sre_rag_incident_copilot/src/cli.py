"""Command-line interface for the SRE RAG Incident Copilot."""

import json
import sys
from pathlib import Path

# Handle imports for both direct script execution and module execution
if __name__ == "__main__":
    # When run as: python src/cli.py
    sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from copilot import IncidentCopilot
from llm_provider import get_llm_provider


def load_sample_incidents(incidents_file: Path) -> list:
    """Load sample incidents from JSON file.

    Args:
        incidents_file: Path to incidents JSON file.

    Returns:
        List of incident dictionaries.

    Raises:
        FileNotFoundError: If incidents file not found.
    """
    if not incidents_file.exists():
        raise FileNotFoundError(f"Incidents file not found: {incidents_file}")

    with open(incidents_file) as f:
        return json.load(f)


def demo_mode(copilot: IncidentCopilot) -> None:
    """Run demonstration with sample incidents.

    Args:
        copilot: Configured IncidentCopilot instance.
    """
    print("\n" + "=" * 70)
    print("SRE RAG INCIDENT COPILOT - DEMO MODE")
    print("=" * 70)

    # Load sample incidents
    try:
        incidents = load_sample_incidents(Config.SAMPLE_INCIDENTS_FILE)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Analyze first 3 incidents
    for i, incident in enumerate(incidents[:3], 1):
        print(f"\n{'-' * 70}")
        print(f"Incident {i}/{min(3, len(incidents))}: {incident['id']}")
        print(f"{'-' * 70}")
        print(f"Title: {incident['title']}")
        print(f"Description: {incident['description'][:100]}...")

        # Analyze
        analysis = copilot.analyze_incident(
            title=incident["title"],
            description=incident["description"],
        )

        # Display results
        print(f"\nAnalysis Results:")
        print(f"  Category: {analysis.category}")
        print(f"  Urgency: {analysis.urgency}")
        print(f"  Confidence: {analysis.confidence_score:.2f}")
        print(f"  Relevant Sources: {', '.join(analysis.relevant_sources)}")
        print(f"\n  First Checks:")
        for check in analysis.first_checks:
            print(f"    • {check}")
        print(f"\n  Action Plan:\n    {analysis.action_plan[:200]}...")
        print(f"\n  Escalation: {analysis.escalation_recommendation}")


def interactive_mode(copilot: IncidentCopilot) -> None:
    """Run interactive incident analysis mode.

    Args:
        copilot: Configured IncidentCopilot instance.
    """
    print("\n" + "=" * 70)
    print("SRE RAG INCIDENT COPILOT - INTERACTIVE MODE")
    print("=" * 70)
    print("\nEnter 'quit' to exit\n")

    while True:
        # Get incident title
        title = input("Incident Title: ").strip()

        if title.lower() == "quit":
            print("Exiting...")
            break

        # Get incident description
        description = input("Incident Description: ").strip()

        if not title or not description:
            print("Please provide both title and description.\n")
            continue

        # Analyze
        print("\nAnalyzing incident...")
        analysis = copilot.analyze_incident(title=title, description=description)

        # Display results
        print("\n" + "-" * 70)
        print("ANALYSIS RESULTS")
        print("-" * 70)
        print(f"Category: {analysis.category}")
        print(f"Urgency: {analysis.urgency}")
        print(f"Confidence: {analysis.confidence_score:.2f}")
        print(f"Relevant Sources: {', '.join(analysis.relevant_sources)}")
        print(f"\nFirst Checks:")
        for check in analysis.first_checks:
            print(f"  • {check}")
        print(f"\nAction Plan:\n{analysis.action_plan}")
        print(f"\nEscalation: {analysis.escalation_recommendation}")
        print()


def help_mode() -> None:
    """Display help message."""
    print("\n" + "=" * 70)
    print("SRE RAG INCIDENT COPILOT - HELP")
    print("=" * 70)
    print("""
Usage:
  python src/cli.py <command> [options]

Commands:
  demo                  Run demonstration with sample incidents
  interactive           Run interactive incident analysis mode
  analyze               Analyze a specific incident
  help                  Show this help message

Analyze Command Options:
  --title "..."         Incident title (required)
  --description "..."   Incident description (required)

Examples:
  python src/cli.py demo
  python src/cli.py interactive
  python src/cli.py analyze \\
    --title "High CPU on prod" \\
    --description "CPU at 95% on production server"

Configuration:
  Set LLM_PROVIDER environment variable:
    - LLM_PROVIDER=mock (default, no API required)
    - LLM_PROVIDER=github_models (requires GITHUB_TOKEN)

  Create .env file from .env.example to configure tokens
""")


def main() -> None:
    """Main CLI entry point."""
    # Load configuration
    Config.validate()

    # Get LLM provider
    try:
        llm_provider = get_llm_provider(
            provider_name=Config.LLM_PROVIDER,
            github_token=Config.GITHUB_TOKEN,
            github_model=Config.GITHUB_MODEL,
            github_endpoint=Config.GITHUB_MODELS_ENDPOINT,
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Initialize copilot
    try:
        copilot = IncidentCopilot(
            llm_provider=llm_provider,
            runbooks_dir=str(Config.RUNBOOKS_DIR),
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Parse command
    if len(sys.argv) < 2:
        help_mode()
        return

    command = sys.argv[1].lower()

    if command == "demo":
        demo_mode(copilot)
    elif command == "interactive":
        interactive_mode(copilot)
    elif command == "analyze":
        # Parse analyze arguments
        title = None
        description = None

        for i, arg in enumerate(sys.argv[2:], 1):
            if arg == "--title" and i < len(sys.argv) - 2:
                title = sys.argv[i + 2]
            elif arg == "--description" and i < len(sys.argv) - 2:
                description = sys.argv[i + 2]

        if not title or not description:
            print("Error: --title and --description are required")
            print("Use: python src/cli.py analyze --title '...' --description '...'")
            sys.exit(1)

        analysis = copilot.analyze_incident(title=title, description=description)

        print("\n" + "=" * 70)
        print("INCIDENT ANALYSIS")
        print("=" * 70)
        print(f"Title: {analysis.incident_title}")
        print(f"Category: {analysis.category}")
        print(f"Urgency: {analysis.urgency}")
        print(f"Confidence: {analysis.confidence_score:.2f}")
        print(f"Relevant Sources: {', '.join(analysis.relevant_sources)}")
        print(f"\nFirst Checks:")
        for check in analysis.first_checks:
            print(f"  • {check}")
        print(f"\nAction Plan:\n{analysis.action_plan}")
        print(f"\nEscalation: {analysis.escalation_recommendation}")
        print()

    elif command == "help":
        help_mode()
    else:
        print(f"Unknown command: {command}")
        help_mode()
        sys.exit(1)


if __name__ == "__main__":
    main()
else:
    # Also support direct script execution
    import sys
    if __name__.endswith("cli"):
        # Running as module, imports should work
        pass
