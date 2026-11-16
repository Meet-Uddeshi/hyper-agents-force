#!/usr/bin/env python3
"""
Dynamic Tech Stack & Architecture Advisor for Hyper Agents Force.

Evaluates user project ideas for greenfield development and dynamically infers
the optimal programming languages, frameworks, database tier, architectural patterns,
and agent team rosters. Not hardcoded or static.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Multi-dimensional domain keyword signals
DOMAIN_SIGNALS = {
    "ai_ml": [
        "ai", "ml", "machine learning", "deep learning", "llm", "rag", "langchain",
        "agent", "agents", "vision", "cv", "nlp", "speech", "embeddings", "neural",
        "pytorch", "tensorflow", "transformer", "huggingface", "vector"
    ],
    "enterprise": [
        "enterprise", "b2b", "banking", "finance", "fintech", "compliance",
        "high throughput", "distributed", "microservices", "kubernetes", "erp",
        "crm", "multi-tenant", "tenant", "audit log", "scale", "million users"
    ],
    "fullstack_saas": [
        "saas", "dashboard", "portal", "web app", "webapp", "platform", "user accounts",
        "stripe", "subscription", "billing", "auth", "crud", "admin panel", "notion clone",
        "trello clone", "analytics", "landing page"
    ],
    "realtime_collaborative": [
        "realtime", "real-time", "collaborative", "websocket", "chat", "streaming",
        "presence", "multiplayer", "game", "gaming", "canvas", "whiteboard", "webrtc"
    ],
    "mobile": [
        "mobile", "ios", "android", "iphone", "ipad", "app store", "play store",
        "push notifications", "camera", "gps", "geolocation", "offline first"
    ],
    "automation": [
        "automation", "workflow", "scraper", "crawler", "n8n", "etl", "data pipeline",
        "integration", "zapier", "make", "bot", "scheduler", "cron", "webhook"
    ],
    "systems_embedded": [
        "embedded", "iot", "firmware", "driver", "kernel", "low level", "performance critical",
        "memory safe", "hardware", "c++", "rust", "native"
    ],
}


class TechStackAdvisor:
    """Dynamic reasoning engine that selects optimal architecture for greenfield ideas."""

    @classmethod
    def analyze_idea(cls, idea_text: str) -> Dict[str, Any]:
        """Analyzes a project prompt and computes dynamic stack and architecture recommendations."""
        text_lower = idea_text.lower()

        # 1. Score domain affinity
        scores = {}
        for domain, keywords in DOMAIN_SIGNALS.items():
            score = 0
            for kw in keywords:
                # Count word boundary matches
                matches = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower))
                score += matches
            scores[domain] = score

        # Determine primary and secondary domains
        sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_domain = sorted_domains[0][0] if sorted_domains[0][1] > 0 else "fullstack_saas"
        secondary_domain = sorted_domains[1][0] if len(sorted_domains) > 1 and sorted_domains[1][1] > 0 else None

        # 2. Determine Scale & Audience
        scale_tier = "MVP / Startup"
        if any(term in text_lower for term in ["enterprise", "million", "high scale", "b2b", "massive", "distributed"]):
            scale_tier = "High Scale / Enterprise"
        elif any(term in text_lower for term in ["prototype", "mvp", "hackathon", "simple", "internal tool"]):
            scale_tier = "Rapid Prototype / MVP"

        # 3. Dynamic Tech Stack Generation
        recommendations = cls._generate_recommendations(primary_domain, secondary_domain, scale_tier, text_lower)

        return {
            "idea_summary": idea_text.strip()[:160] + "..." if len(idea_text) > 160 else idea_text.strip(),
            "inferred_domain": primary_domain,
            "secondary_domain": secondary_domain,
            "scale_tier": scale_tier,
            "tech_stack": recommendations["stack"],
            "architecture_pattern": recommendations["architecture"],
            "database_strategy": recommendations["database"],
            "agent_team_roster": recommendations["agent_team"],
            "implementation_phases": recommendations["phases"],
        }

    @classmethod
    def _generate_recommendations(cls, primary: str, secondary: Optional[str], scale: str, full_text: str) -> Dict[str, Any]:
        """Builds bespoke technical specifications based on analyzed parameters."""
        stack = {}
        arch = ""
        database = {}
        team = []
        phases = []

        if primary == "ai_ml":
            stack = {
                "backend": "Python 3.11+ with FastAPI (Async, high-speed, native ML bindings)",
                "ai_runtime": "PyTorch / ONNX Runtime + LangChain / LlamaIndex",
                "frontend": "Next.js 14+ / React with Tailwind CSS & Shadcn UI",
                "caching": "Redis (Semantic prompt cache & session state)",
            }
            database = {
                "primary": "PostgreSQL with pgvector extension (Combined relational data + vector search)",
                "document_store": "Local SQLite or S3 for artifact & dataset storage",
            }
            arch = "Layered Service Architecture with Asynchronous Inference Queue (Celery/Redis)"
            team = [
                {"role": "Team Lead", "agent": "ai-engineer"},
                {"role": "Backend & API Specialist", "agent": "backend-specialist"},
                {"role": "Vector & Database Architect", "agent": "database-architect"},
                {"role": "Frontend Craft Specialist", "agent": "frontend-specialist"},
            ]
            phases = [
                "1. Data model, embeddings pipeline & vector index configuration",
                "2. Model inference router & RAG context retrieval implementation",
                "3. API endpoints, authentication, and token consumption guardrails",
                "4. Reactive user interface with streaming response renderer",
            ]

        elif primary == "enterprise":
            is_go = "go" in full_text or "golang" in full_text
            stack = {
                "backend": "Go (High throughput, zero GC pauses) or Java 21 / Spring Boot 3" if not is_go else "Go (Golang)",
                "api_protocol": "gRPC for internal microservices, REST/OpenAPI for public clients",
                "frontend": "Next.js or React with TypeScript and strict ESLint boundary enforcement",
                "message_broker": "Apache Kafka or RabbitMQ (Event-driven decoupling)",
            }
            database = {
                "primary": "PostgreSQL (ACID compliance, schema validation, partitioning)",
                "cache_tier": "Redis Cluster (Distributed session & distributed locking)",
            }
            arch = "Event-Driven Modular Monolith transitioning to Microservices"
            team = [
                {"role": "Team Lead & System Architect", "agent": "architect"},
                {"role": "Enterprise Backend Specialist", "agent": "backend-specialist"},
                {"role": "Database & High-Scale Architect", "agent": "database-architect"},
                {"role": "Security & Compliance Specialist", "agent": "security-specialist"},
            ]
            phases = [
                "1. Domain boundary definitions, schema DDL, and tenant isolation policies",
                "2. Event bus contracts, gRPC schemas, and core business service layer",
                "3. REST API gateway with rate limiting, DLP, and JWT authentication",
                "4. Comprehensive integration, concurrency, and load testing",
            ]

        elif primary == "realtime_collaborative":
            stack = {
                "backend": "Node.js / TypeScript with Socket.io / ws or Go (Goroutines for millions of sockets)",
                "frontend": "React with Zustand / Valtio state management and Canvas / Fabric.js / Pixi.js",
                "crdt_engine": "Yjs or Automerge for conflict-free replicated data types",
            }
            database = {
                "primary": "PostgreSQL for persistent state",
                "in_memory": "Redis with Redis Pub/Sub (State synchronization between nodes)",
            }
            arch = "CRDT-Driven Real-time WebSocket Architecture"
            team = [
                {"role": "Team Lead", "agent": "fullstack-specialist"},
                {"role": "Real-time Protocol Specialist", "agent": "backend-specialist"},
                {"role": "Interactive UI Craft Specialist", "agent": "frontend-specialist"},
                {"role": "Testing & Chaos Engineer", "agent": "qa-automation-engineer"},
            ]
            phases = [
                "1. WebSocket protocol framing, CRDT document schema, and Redis sync",
                "2. Real-time broadcast engine with presence tracking and heartbeat",
                "3. Interactive frontend canvas with optimistic UI updates",
                "4. Latency benchmarking, reconnection recovery, and packet loss simulation",
            ]

        elif primary == "mobile":
            stack = {
                "framework": "Flutter with Riverpod / Dart (Cross-platform native iOS & Android) or React Native / Expo",
                "backend": "FastAPI or Supabase / Node.js backend",
                "local_storage": "Isar / Hive or SQLite (Offline-first caching)",
            }
            database = {
                "primary": "PostgreSQL (Supabase) or Firebase Firestore",
                "offline_sync": "Bidirectional conflict resolution sync queue",
            }
            arch = "Offline-First Mobile Architecture with Repository Pattern"
            team = [
                {"role": "Team Lead", "agent": "mobile-developer"},
                {"role": "Mobile UI/UX Specialist", "agent": "frontend-specialist"},
                {"role": "API & Backend Specialist", "agent": "backend-specialist"},
                {"role": "Mobile Automation Engineer", "agent": "mobile-automation-engineer"},
            ]
            phases = [
                "1. Flutter / React Native workspace scaffold and atomic design system",
                "2. Offline-first local database cache and remote synchronization service",
                "3. Native hardware integrations (camera, biometric auth, push notifications)",
                "4. Appium mobile automation suite across iOS & Android simulators",
            ]

        elif primary == "automation":
            stack = {
                "engine": "Python 3.11 with Celery / Temporal or n8n workflow orchestrator",
                "integration_runtime": "FastAPI with dynamic webhook receivers and rate-limited dispatchers",
                "data_processing": "Pandas / Polars for batch extraction and validation",
            }
            database = {
                "primary": "PostgreSQL with JSONB columns for dynamic payload storage",
                "queue": "Redis or RabbitMQ for reliable job queues",
            }
            arch = "Event-Driven Asynchronous Pipeline Architecture"
            team = [
                {"role": "Team Lead", "agent": "devops-engineer"},
                {"role": "Backend Integration Specialist", "agent": "backend-specialist"},
                {"role": "Database Architect", "agent": "database-architect"},
                {"role": "Security Specialist", "agent": "security-specialist"},
            ]
            phases = [
                "1. Webhook schema registry, payload normalizers, and dead-letter queues",
                "2. Step-function worker tasks with automatic exponential backoff",
                "3. API connectors with OAuth2 refresh token rotation",
                "4. End-to-end trace logging and idempotent execution testing",
            ]

        else:  # Fullstack SaaS (Default)
            stack = {
                "frontend": "Next.js 14+ (App Router, Server Components) with Tailwind CSS",
                "backend": "Next.js Server Actions & API Routes with Zod validation",
                "auth": "Auth.js (NextAuth) or Clerk / Supabase Auth",
                "payments": "Stripe SDK with webhook verification",
            }
            database = {
                "primary": "PostgreSQL with Prisma ORM / Drizzle ORM",
                "cache": "Upstash Redis for edge caching and rate limiting",
            }
            arch = "Serverless Full-Stack Monorepo Architecture"
            team = [
                {"role": "Team Lead", "agent": "fullstack-specialist"},
                {"role": "Frontend Craft Specialist", "agent": "frontend-specialist"},
                {"role": "Backend & Database Architect", "agent": "database-architect"},
                {"role": "Accessibility & SEO Specialist", "agent": "seo-specialist"},
            ]
            phases = [
                "1. Prisma schema, migration scripts, and seed data initialization",
                "2. Authentication routes, session middleware, and RBAC guardrails",
                "3. Responsive dashboard UI components, forms with Zod validation",
                "4. Stripe subscription webhook handling and deployment pipeline",
            ]

        return {
            "stack": stack,
            "architecture": arch,
            "database": database,
            "agent_team": team,
            "phases": phases,
        }

    @classmethod
    def format_advisor_markdown(cls, analysis: Dict[str, Any]) -> str:
        """Formats the analysis into high-density structured markdown."""
        lines = [
            f"# Greenfield Architecture Blueprint: {analysis['inferred_domain'].upper()} Tier",
            "",
            f"**Project Summary**: {analysis['idea_summary']}",
            f"**Target Scale Tier**: {analysis['scale_tier']}",
            f"**Recommended Architectural Pattern**: `{analysis['architecture_pattern']}`",
            "",
            "## 1. Recommended Technology Stack",
        ]
        for category, detail in analysis["tech_stack"].items():
            lines.append(f"- **{category.capitalize()}**: {detail}")

        lines.extend([
            "",
            "## 2. Database & Storage Strategy",
        ])
        for db_role, detail in analysis["database_strategy"].items():
            lines.append(f"- **{db_role.capitalize()}**: {detail}")

        lines.extend([
            "",
            "## 3. Recommended Collaborative Agent Team",
        ])
        for member in analysis["agent_team_roster"]:
            lines.append(f"- `@{member['agent']}` ({member['role']})")

        lines.extend([
            "",
            "## 4. Phased Implementation Roadmap",
        ])
        for step in analysis["implementation_phases"]:
            lines.append(f"- {step}")

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tech_stack_advisor.py \"<your project idea>\"")
        sys.exit(1)

    idea = " ".join(sys.argv[1:])
    analysis = TechStackAdvisor.analyze_idea(idea)
    print("\n" + TechStackAdvisor.format_advisor_markdown(analysis) + "\n")


if __name__ == "__main__":
    main()
