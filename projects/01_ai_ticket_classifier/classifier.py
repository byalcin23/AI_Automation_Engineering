"""
Rule-based ticket classifier for SRE/infrastructure tickets.

This module provides a simple, production-ready classifier for SRE and
infrastructure tickets. It categorizes tickets and assigns priority levels
without requiring external LLM APIs.

Example:
    >>> classifier = TicketClassifier()
    >>> result = classifier.classify(
    ...     "Database replication lag detected",
    ...     "Monitoring shows 45 second lag on replica-02. P1 impact."
    ... )
    >>> print(f"{result.category}: {result.priority}")
    incident: high
"""

from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Result of ticket classification.

    Attributes:
        category: The ticket category (incident, deployment, config_change,
                  access_request, investigation)
        priority: The priority level (critical, high, medium, low)
        confidence: Confidence score between 0.0 and 1.0
        recommended_action: Suggested next action for the ticket
    """

    category: str
    priority: str
    confidence: float
    recommended_action: str


class TicketClassifier:
    """Rule-based classifier for SRE and infrastructure tickets.

    This classifier uses keyword matching to categorize tickets and determine
    their priority level. It requires no external APIs or LLM integration.

    Attributes:
        INCIDENT_KEYWORDS: Keywords for detecting incident tickets
        DEPLOYMENT_KEYWORDS: Keywords for detecting deployment tickets
        CONFIG_CHANGE_KEYWORDS: Keywords for detecting config change tickets
        ACCESS_REQUEST_KEYWORDS: Keywords for detecting access requests
        INVESTIGATION_KEYWORDS: Keywords for detecting investigation requests
        CRITICAL_INDICATORS: Keywords indicating critical priority
        HIGH_INDICATORS: Keywords indicating high priority
        MEDIUM_INDICATORS: Keywords indicating medium priority
    """

    # Keywords for incident tickets
    INCIDENT_KEYWORDS = {
        "keywords": [
            "down", "outage", "error", "failure", "crashed", "not responding",
            "critical", "p1", "emergency", "urgent", "fire", "broken", "stuck",
            "lag", "spike", "high cpu", "high memory", "disk full", "timeout",
            "restart", "failing", "alert", "triggered", "attack", "breach"
        ],
        "weight": 1.0
    }

    # Keywords for deployment tickets
    DEPLOYMENT_KEYWORDS = {
        "keywords": [
            "deploy", "release", "rollout", "blue-green", "canary", "version",
            "upgrade", "push", "merge", "ci/cd", "pipeline", "build", "docker",
            "kubernetes", "helm", "terraform", "cloudformation",
            "infrastructure as code"
        ],
        "weight": 1.0
    }

    # Keywords for config change tickets
    CONFIG_CHANGE_KEYWORDS = {
        "keywords": [
            "config", "update", "change", "threshold", "parameter", "setting",
            "prometheus", "alert", "monitoring", "dashboard", "grafana",
            "logging", "retention", "policy", "rule", "flag"
        ],
        "weight": 1.0
    }

    # Keywords for access request tickets
    ACCESS_REQUEST_KEYWORDS = {
        "keywords": [
            "access", "permission", "role", "ssh", "api key", "token",
            "credential", "iam", "rbac", "certificate", "secret", "vault", "auth"
        ],
        "weight": 1.0
    }

    # Keywords for investigation tickets
    INVESTIGATION_KEYWORDS = {
        "keywords": [
            "investigate", "root cause", "analysis", "debug", "trace", "log",
            "inspect", "unusual", "anomaly", "suspicious", "security",
            "audit", "check", "review", "diagnose"
        ],
        "weight": 1.0
    }

    # Keywords indicating critical priority
    CRITICAL_INDICATORS = {
        "keywords": ["p0", "critical", "sev-1", "prod-down", "outage", "emergency"],
        "weight": 1.0
    }

    # Keywords indicating high priority
    HIGH_INDICATORS = {
        "keywords": ["p1", "high", "sev-2", "production", "prod", "urgent", "impact"],
        "weight": 0.8
    }

    # Keywords indicating medium priority
    MEDIUM_INDICATORS = {
        "keywords": ["p2", "medium", "sev-3", "staging", "test"],
        "weight": 0.5
    }

    def __init__(self):
        """Initialize the ticket classifier."""
        pass

    def classify(self, title: str, description: str) -> ClassificationResult:
        """Classify a ticket based on title and description.

        Args:
            title: The ticket title/summary
            description: The ticket description/body

        Returns:
            ClassificationResult containing category, priority, confidence,
            and recommended action

        Example:
            >>> classifier = TicketClassifier()
            >>> result = classifier.classify(
            ...     "P0 - API Servers Down",
            ...     "All API servers not responding. Emergency response needed."
            ... )
            >>> print(result.priority)
            critical
        """
        # Combine and normalize text for analysis
        combined_text = f"{title} {description}".lower()

        # Calculate category scores
        scores = {
            "incident": self._score_category(combined_text, self.INCIDENT_KEYWORDS),
            "deployment": self._score_category(
                combined_text, self.DEPLOYMENT_KEYWORDS
            ),
            "config_change": self._score_category(
                combined_text, self.CONFIG_CHANGE_KEYWORDS
            ),
            "access_request": self._score_category(
                combined_text, self.ACCESS_REQUEST_KEYWORDS
            ),
            "investigation": self._score_category(
                combined_text, self.INVESTIGATION_KEYWORDS
            ),
        }

        # Find highest scoring category
        category = max(scores, key=scores.get)
        category_confidence = scores[category]

        # If no strong match, default to investigation
        if category_confidence < 0.3:
            category = "investigation"
            category_confidence = 0.3

        # Determine priority
        priority, priority_confidence = self._determine_priority(combined_text)

        # Combine confidences (weighted average)
        overall_confidence = (category_confidence + priority_confidence) / 2
        overall_confidence = min(0.99, max(0.0, overall_confidence))

        # Get recommended action
        action = self._get_recommended_action(category, priority, title, description)

        return ClassificationResult(
            category=category,
            priority=priority,
            confidence=round(overall_confidence, 2),
            recommended_action=action,
        )

    def _score_category(self, text: str, category_keywords: dict) -> float:
        """Score text against category keywords.

        Calculates how well the text matches a category based on keyword
        frequency.

        Args:
            text: The normalized text to score
            category_keywords: Dictionary with 'keywords' list and 'weight'

        Returns:
            Score between 0.0 and 1.0
        """
        keywords = category_keywords["keywords"]
        matches = sum(1 for keyword in keywords if keyword in text)

        if not keywords or matches == 0:
            return 0.0

        # Score based on: number of matches / total keywords
        # Minimum 0.3 if any match found
        score = min(1.0, matches / len(keywords))
        score = max(score, 0.3) if matches > 0 else score
        return score * category_keywords["weight"]

    def _determine_priority(self, text: str) -> tuple:
        """Determine priority level from text.

        Args:
            text: The normalized text to analyze

        Returns:
            Tuple of (priority_level, confidence_score)
            Priority level is one of: critical, high, medium, low
        """
        # Check critical indicators
        critical_score = self._score_category(text, self.CRITICAL_INDICATORS)
        if critical_score > 0.5:
            return "critical", critical_score

        # Check high indicators
        high_score = self._score_category(text, self.HIGH_INDICATORS)
        if high_score > 0.5:
            return "high", high_score

        # Check medium indicators
        medium_score = self._score_category(text, self.MEDIUM_INDICATORS)
        if medium_score > 0.3:
            return "medium", medium_score

        # Default to low
        return "low", 0.5

    def _get_recommended_action(
        self, category: str, priority: str, title: str, description: str
    ) -> str:
        """Generate recommended action based on classification.

        Args:
            category: The ticket category
            priority: The ticket priority
            title: The ticket title (for context)
            description: The ticket description (for context)

        Returns:
            A string with recommended next actions
        """
        # Decision matrix: (category, priority) -> action
        actions = {
            ("incident", "critical"): (
                "1. Check status dashboards immediately. "
                "2. Page on-call engineer. 3. Review recent deployments."
            ),
            ("incident", "high"): (
                "1. Monitor dashboards. 2. Check logs for errors. "
                "3. Investigate related components."
            ),
            ("incident", "medium"): (
                "1. Review logs and metrics. 2. Identify root cause. "
                "3. Prepare mitigation plan."
            ),
            ("incident", "low"): "1. Log issue for investigation. 2. Monitor for recurrence.",
            ("deployment", "critical"): (
                "1. Review deployment plan. 2. Ensure rollback procedure is ready. "
                "3. Execute with caution."
            ),
            ("deployment", "high"): (
                "1. Review release notes. 2. Run smoke tests. "
                "3. Monitor after deployment."
            ),
            ("deployment", "medium"): (
                "1. Verify tests pass. 2. Follow standard deployment procedure."
            ),
            ("deployment", "low"): "1. Schedule deployment window. 2. Notify stakeholders.",
            ("config_change", "critical"): (
                "1. Review impact analysis. 2. Test in staging. 3. Plan rollback."
            ),
            ("config_change", "high"): (
                "1. Validate change in test environment. 2. Plan monitoring."
            ),
            ("config_change", "medium"): "1. Document change. 2. Deploy to staging first.",
            ("config_change", "low"): (
                "1. Update configuration management system. 2. Document change."
            ),
            ("access_request", "critical"): (
                "1. Expedite approval. 2. Provision immediately. "
                "3. Verify security requirements."
            ),
            ("access_request", "high"): (
                "1. Review security requirements. 2. Provision access."
            ),
            ("access_request", "medium"): (
                "1. Follow standard approval process. 2. Provision access."
            ),
            ("access_request", "low"): "1. Queue for next access review batch.",
            ("investigation", "critical"): (
                "1. Assign senior engineer. 2. Collect all relevant logs. "
                "3. Escalate if security issue."
            ),
            ("investigation", "high"): (
                "1. Assign engineer. 2. Gather data. 3. Document findings."
            ),
            ("investigation", "medium"): (
                "1. Schedule investigation. 2. Collect logs and metrics."
            ),
            ("investigation", "low"): "1. Add to backlog for future investigation.",
        }

        # Get specific action or fall back to generic
        action = actions.get(
            (category, priority),
            f"Review and handle {category} ticket with {priority} priority.",
        )

        return action
