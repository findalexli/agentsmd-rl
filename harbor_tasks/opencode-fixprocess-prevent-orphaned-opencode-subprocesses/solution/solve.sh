#!/bin/bash
set -e

cd /workspace/myrepo

# Fix the bug: change a - b to a + b
sed -i 's/return a - b/return a + b/' src/calculator.py

# Update the documentation
sed -i 's/The add() function has a bug: it subtracts instead of adding/The add() function is fixed and works correctly/' CLAUDE.md

# Commit the fix
git add src/calculator.py CLAUDE.md
git commit -m "Fix add function: was subtracting instead of adding"
