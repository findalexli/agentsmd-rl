FROM python:3.11-slim

# Install git and basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python testing tools and build tools
RUN pip install --no-cache-dir pytest ruff mypy hatchling

# Copy repo into container so it's writable
COPY repo /workspace/repo

# Set up the repo directory
WORKDIR /workspace/repo

# Set PYTHONPATH so the repo package can be found
ENV PYTHONPATH=/workspace/repo/src

# Set REPO path for solve.sh and other scripts
ENV REPO=/workspace/repo

# The test files will be mounted at /tests

# Default command runs the tests
CMD ["bash", "/tests/test.sh"]
