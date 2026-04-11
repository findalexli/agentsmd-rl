#!/bin/bash
# Gold patch for fixing sum_numbers empty list handling

cat > /workspace/task_repo/mymath.py << 'EOF'
"""Simple math utilities module."""


def sum_numbers(numbers):
    """Sum a list of numbers.

    Args:
        numbers: A list of numbers to sum.

    Returns:
        The sum of all numbers in the list.

    Raises:
        TypeError: If numbers is not a list.
    """
    # Fixed: Empty list returns 0 (mathematically correct)
    if not numbers:
        return 0

    total = 0
    for n in numbers:
        total += n
    return total


def average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return None
    return sum_numbers(numbers) / len(numbers)
EOF
