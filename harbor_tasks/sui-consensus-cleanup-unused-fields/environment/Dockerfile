FROM python:3.11-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone requests repo at a specific commit
WORKDIR /workspace
RUN git clone --depth 1 https://github.com/psf/requests.git requests

# Set working directory to the repo
WORKDIR /workspace/requests

# Install test dependencies but DON'T install requests properly (create a bug scenario)
# The package is cloned but not installed in editable mode - this creates a failure scenario
RUN pip install pytest pytest-httpbin httpbin pytest-mock pytest-xdist trustme ruff
# Intentionally broken: requests is not installed, creating a scenario where imports fail
# This will be fixed by solve.sh which runs 'pip install -e .'

# Create test directory
RUN mkdir -p /tests /logs/verifier

# Default to bash
CMD ["bash"]
