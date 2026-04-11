FROM python:3.11-slim

# Install git for any potential git operations
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install pytest for testing
RUN pip install pytest

# Set working directory to where the repo will be mounted
WORKDIR /workspace/task_repo

# Copy the repo files
COPY mymath.py /workspace/task_repo/mymath.py

# Default command runs tests
CMD ["python3", "-m", "pytest", "-v"]
