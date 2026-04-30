#!/bin/bash
# Gold patch to fix the divide-by-zero bug in calculator.py

cd /workspace/calculator

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
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
EOF

git add calculator.py
git commit -m "Fix divide by zero bug - raise ValueError instead of crashing"
