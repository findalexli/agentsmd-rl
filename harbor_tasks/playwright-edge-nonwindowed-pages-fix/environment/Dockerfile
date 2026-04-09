FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Create a minimal example repo for validation
RUN mkdir -p /workspace/example-repo && \
    cd /workspace/example-repo && \
    git init && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/example-repo

# Create a simple Python module with a bug
RUN cat > calculator.py << 'EOF'
def add(a, b):
    """Add two numbers - BUG: subtracts instead of adds."""
    return a - b  # BUG: should be a + b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b
EOF

# Commit the buggy version as base
RUN git add calculator.py && \
    git commit -m "Initial commit with bug"

ENV PYTHONPATH="/workspace/example-repo"

# Verifier output directory
RUN mkdir -p /logs/verifier
