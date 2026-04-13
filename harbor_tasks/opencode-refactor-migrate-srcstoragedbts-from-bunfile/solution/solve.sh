#!/bin/bash
# Gold patch for calculator division by zero fix

cat > calculator.py << 'EOF'
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
    """Divide a by b, raising ZeroDivisionError if b is 0."""
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b
EOF
