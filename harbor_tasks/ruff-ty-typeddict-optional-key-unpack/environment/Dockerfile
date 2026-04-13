FROM python:3.10-slim

# Install dependencies
RUN pip install pytest ruff mypy

# Set up the repository
WORKDIR /workspace/calculator

# Copy repo files
COPY calculator.py .
COPY tests/ tests/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Default working directory for tests
WORKDIR /workspace/calculator
