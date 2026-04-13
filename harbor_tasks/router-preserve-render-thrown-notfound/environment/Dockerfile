FROM python:3.11-slim

WORKDIR /workspace/example-repo

# Install dependencies
RUN pip install --no-cache-dir \
    pytest \
    ruff \
    mypy \
    requests

# Clone the repo at base commit (this would normally be done by the task runner)
# For demo purposes, we'll create a minimal repo structure
RUN mkdir -p src tests

# The repo will be mounted or cloned here at runtime
# We don't COPY here - the repo is mounted via docker run -v

# Default command runs the tests
CMD ["bash", "/tests/test.sh"]
