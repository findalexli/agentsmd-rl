FROM python:3.11-slim

# Install git and pytest
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/* && \
    pip install pytest

WORKDIR /workspace/myrepo

# Create a simple Python module with a bug and a CLAUDE.md
RUN mkdir -p /workspace/myrepo/src && \
    cat > /workspace/myrepo/src/calculator.py << 'EOF'
def add(a, b):
    """Add two numbers - but has a bug: it subtracts instead."""
    return a - b  # BUG: should be a + b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b
EOF

# Create CLAUDE.md documenting the module
RUN cat > /workspace/myrepo/CLAUDE.md << 'EOF'
# Calculator Module

This module provides basic arithmetic operations.

## Known Issues

- The add() function has a bug: it subtracts instead of adding
EOF

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
