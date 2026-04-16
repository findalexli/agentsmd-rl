FROM python:3.12-slim

# Install git and basic utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/SeleniumHQ/selenium.git selenium \
    && cd selenium \
    && git checkout 85bc60cdb48682563d7dbdc1f175bffc91fb1231

# Install minimal Python dependencies for testing
RUN pip install --no-cache-dir pytest

# Set up the Python path so we can import from the selenium package
ENV PYTHONPATH=/workspace/selenium/py

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/selenium
