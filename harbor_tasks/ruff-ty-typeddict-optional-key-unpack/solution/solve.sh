#!/bin/bash
# Fix for divide by zero bug

cd /workspace/calculator

cat > calculator.py << 'EOF'
"""Simple calculator module."""


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
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(base, exponent):
    """Raise base to the power of exponent."""
    result = 1
    for _ in range(exponent):
        result *= base
    return result
EOF
