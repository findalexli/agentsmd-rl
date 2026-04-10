FROM python:3.11-slim

# Set working directory to match the expected path
WORKDIR /workspace/repo

# Install any additional tools needed for testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for testing
RUN pip install --no-cache-dir pytest

# Create the buggy base main.py file inline
RUN echo 'import os' > /workspace/repo/main.py && \
    echo 'import sys' >> /workspace/repo/main.py && \
    echo '' >> /workspace/repo/main.py && \
    echo 'def process_file(filepath):' >> /workspace/repo/main.py && \
    echo '    try:' >> /workspace/repo/main.py && \
    echo '        with open(filepath, "r") as f:' >> /workspace/repo/main.py && \
    echo '            content = f.read()' >> /workspace/repo/main.py && \
    echo '        return content.upper()' >> /workspace/repo/main.py && \
    echo '    except:' >> /workspace/repo/main.py && \
    echo '        return None' >> /workspace/repo/main.py

# Default command
CMD ["python3"]
