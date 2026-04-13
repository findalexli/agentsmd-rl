FROM python:3.11-slim

WORKDIR /workspace/calc-repo

# Install dependencies
RUN pip install pytest pytest-cov black ruff mypy

# Note: The actual repo will be mounted at runtime
# This Dockerfile sets up the environment only

# Default command
CMD ["bash"]
