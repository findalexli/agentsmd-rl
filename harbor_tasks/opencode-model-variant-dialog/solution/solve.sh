#!/bin/bash
# Gold patch: Fix the divide function to handle division by zero

set -e

mkdir -p /workspace/calc-repo
cd /workspace/calc-repo

# Create src directory and the fixed calc.py
mkdir -p src
cat > src/calc.py << 'EOF'
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide a by b, handling division by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
EOF

# Create tests directory with the test file
mkdir -p tests
cat > tests/test_calc.py << 'EOF'
"""Tests for the calculator module."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calc import add, subtract, multiply, divide


def test_add():
    """Test addition."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    """Test subtraction."""
    assert subtract(5, 3) == 2
    assert subtract(10, 5) == 5
    assert subtract(0, 0) == 0


def test_multiply():
    """Test multiplication."""
    assert multiply(4, 5) == 20
    assert multiply(0, 5) == 0
    assert multiply(-2, 3) == -6


def test_divide():
    """Test division."""
    assert divide(10, 2) == 5
    assert divide(0, 5) == 0
    assert divide(7, 2) == 3.5


def test_divide_by_zero():
    """Test that divide raises ValueError on division by zero."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
EOF

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "calc-repo"
version = "0.1.0"
description = "Simple calculator module"
requires-python = ">=3.8"
dependencies = []

[project.optional-dependencies]
test = ["pytest", "pytest-cov"]
dev = ["black", "ruff", "mypy"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
EOF

# Update CLAUDE.md with the fix documentation
mkdir -p .claude
cat > .claude/CLAUDE.md << 'EOF'
# Calculator Module Conventions

## Error Handling

All mathematical operations must validate inputs and raise appropriate exceptions:
- Division by zero must raise `ValueError` with a clear message
- Invalid types should raise `TypeError`

## Testing

Run tests with: `pytest tests/ -v`
Run linting with: `ruff check src/`
Run type checking with: `mypy src/`
EOF

echo "Fix applied successfully"
