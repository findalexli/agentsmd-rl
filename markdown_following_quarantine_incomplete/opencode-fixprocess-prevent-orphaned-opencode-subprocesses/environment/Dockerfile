FROM python:3.11-slim

# Install git and pytest
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/* && \
    pip install pytest pytest-json-ctrf

# Ensure Harbor verifier log directory exists
RUN mkdir -p /logs/verifier

WORKDIR /workspace/myrepo

# Create a simple Python module with a bug and a CLAUDE.md
RUN mkdir -p /workspace/myrepo/src && \
    printf 'def add(a, b):\n    """Add two numbers - but has a bug: it subtracts instead."""\n    return a - b  # BUG: should be a + b\n\ndef multiply(a, b):\n    """Multiply two numbers."""\n    return a * b\n' > /workspace/myrepo/src/calculator.py

# Create CLAUDE.md documenting the module
RUN printf '# Calculator Module\n\nThis module provides basic arithmetic operations.\n\n## Known Issues\n\n- The add() function has a bug: it subtracts instead of adding\n' > /workspace/myrepo/CLAUDE.md

# Mark the directory as safe for git
RUN git config --global --add safe.directory /workspace/myrepo && \
    git config --global user.email "test@test.com" && \
    git config --global user.name "Test User"

# Initialize a git repo at base commit
RUN cd /workspace/myrepo && \
    git init && \
    git add . && \
    git commit -m "Initial commit with bug"

WORKDIR /workspace/myrepo
