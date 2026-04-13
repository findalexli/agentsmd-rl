FROM python:3.11-slim

WORKDIR /workspace/repo

# Install testing dependencies
RUN pip install pytest

# Copy the buggy code
COPY string_utils.py /workspace/repo/string_utils.py

# Default command
CMD ["bash"]
