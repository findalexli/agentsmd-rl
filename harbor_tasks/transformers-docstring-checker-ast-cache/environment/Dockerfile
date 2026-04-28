# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

WORKDIR /workspace/calculator

# Install git for cloning
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Initialise the inline repo
RUN mkdir -p /workspace/calculator && \
    cd /workspace/calculator && \
    git init && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

# Create initial calculator.py with the bug (Dockerfile heredoc — needs syntax=1.4)
COPY <<'EOF' /workspace/calculator/calculator.py
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide a by b."""
    # BUG: No handling for division by zero
    return a / b
EOF

COPY <<'EOF' /workspace/calculator/test_calculator.py
import unittest
from calculator import add, subtract, multiply, divide

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)

    def test_multiply(self):
        self.assertEqual(multiply(4, 3), 12)

    def test_divide(self):
        self.assertEqual(divide(10, 2), 5)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)

if __name__ == "__main__":
    unittest.main()
EOF

COPY <<'EOF' /workspace/calculator/requirements.txt
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
EOF

COPY <<'EOF' /workspace/calculator/pyproject.toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "calculator"
version = "0.1.0"
description = "Simple calculator module"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
EOF

# Commit the base version
RUN cd /workspace/calculator && \
    git add . && \
    git commit -m "Initial calculator with bug"

# Install Python dependencies including linting tools
RUN pip install --no-cache-dir pytest black flake8 mypy ruff

RUN mkdir -p /logs/verifier
