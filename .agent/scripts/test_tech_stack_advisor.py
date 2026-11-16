#!/usr/bin/env python3
"""
Unit tests for Dynamic Tech Stack & Architecture Advisor.
"""

import sys
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.tech_stack_advisor import TechStackAdvisor


def test_ai_ml_idea_recommendation():
    """Verify AI/ML idea dynamically recommends Python, FastAPI, and vector DB."""
    prompt = "I have an idea for an AI vision and NLP platform using custom PyTorch transformer models and RAG vector search."
    analysis = TechStackAdvisor.analyze_idea(prompt)

    assert analysis["inferred_domain"] == "ai_ml"
    assert "Python" in analysis["tech_stack"]["backend"]
    assert "FastAPI" in analysis["tech_stack"]["backend"]
    assert "pgvector" in analysis["database_strategy"]["primary"]
    assert any(m["agent"] == "ai-engineer" for m in analysis["agent_team_roster"])


def test_enterprise_banking_recommendation():
    """Verify high-scale enterprise idea dynamically recommends Go/Java and Kafka."""
    prompt = "I have an idea for high scale enterprise B2B fintech banking service handling millions of payments."
    analysis = TechStackAdvisor.analyze_idea(prompt)

    assert analysis["inferred_domain"] == "enterprise"
    assert analysis["scale_tier"] == "High Scale / Enterprise"
    assert ("Go" in analysis["tech_stack"]["backend"] or "Java" in analysis["tech_stack"]["backend"])
    assert "Kafka" in analysis["tech_stack"]["message_broker"]
    assert any(m["agent"] == "architect" for m in analysis["agent_team_roster"])


def test_mobile_offline_recommendation():
    """Verify mobile idea recommends Flutter/React Native and offline-first storage."""
    prompt = "I have an idea for a cross-platform mobile app for iOS and Android with camera and offline synchronization."
    analysis = TechStackAdvisor.analyze_idea(prompt)

    assert analysis["inferred_domain"] == "mobile"
    assert ("Flutter" in analysis["tech_stack"]["framework"] or "React Native" in analysis["tech_stack"]["framework"])
    assert any(m["agent"] == "mobile-developer" for m in analysis["agent_team_roster"])


def test_markdown_formatting():
    """Verify markdown output format contains required sections."""
    prompt = "A simple SaaS dashboard for customer invoices with Stripe billing."
    analysis = TechStackAdvisor.analyze_idea(prompt)
    md = TechStackAdvisor.format_advisor_markdown(analysis)

    assert "# Greenfield Architecture Blueprint" in md
    assert "Recommended Technology Stack" in md
    assert "Database & Storage Strategy" in md
    assert "Recommended Collaborative Agent Team" in md


if __name__ == "__main__":
    test_ai_ml_idea_recommendation()
    test_enterprise_banking_recommendation()
    test_mobile_offline_recommendation()
    test_markdown_formatting()
    print("All tech stack advisor tests passed successfully.")
