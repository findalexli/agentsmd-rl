"""Behavioral checks for nestjs-cqrs-starter-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nestjs-cqrs-starter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| MySQL 8    | `docker run -d -e MYSQL_ROOT_PASSWORD=Admin12345 -e MYSQL_USER=usr -e MYSQL_PASSWORD=User12345 -e MYSQL_DATABASE=development -e MYSQL_AUTHENTICATION_PLUGIN=mysql_native_password -p 3306' in text, "expected to find: " + '| MySQL 8    | `docker run -d -e MYSQL_ROOT_PASSWORD=Admin12345 -e MYSQL_USER=usr -e MYSQL_PASSWORD=User12345 -e MYSQL_DATABASE=development -e MYSQL_AUTHENTICATION_PLUGIN=mysql_native_password -p 3306'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'NestJS CQRS Microservices Starter — a monorepo demonstrating an advanced microservice architecture with GraphQL (Apollo Federation), Domain-Driven Design (DDD), and the Command Query Responsibility Se' in text, "expected to find: " + 'NestJS CQRS Microservices Starter — a monorepo demonstrating an advanced microservice architecture with GraphQL (Apollo Federation), Domain-Driven Design (DDD), and the Command Query Responsibility Se'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Events**: Domain events are published after successful command execution and handled asynchronously by `EventHandler` classes. Cross-service events flow through EventStore persistent subscriptions' in text, "expected to find: " + '- **Events**: Domain events are published after successful command execution and handled asynchronously by `EventHandler` classes. Cross-service events flow through EventStore persistent subscriptions'[:80]

