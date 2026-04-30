FROM python:3.12-bookworm

# Install Node.js via NodeSource
RUN apt-get update --allow-insecure-repositories || apt-get update --allow-unauthenticated || true && \
    apt-get install -y --allow-unauthenticated curl ca-certificates git nodejs npm || \
    (curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
     apt-get install -y nodejs) && \
    rm -rf /var/lib/apt/lists/* || true

# Install uv for Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set up working directory
WORKDIR /workspace

# Create logs directory for Harbor
RUN mkdir -p /logs/verifier

# Clone Playwright repo at base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright \
    && cd /workspace/playwright \
    && git checkout 8710e613f8297cebe33c4f6a745999ab4e4907aa

# Install Node.js dependencies
WORKDIR /workspace/playwright
RUN npm ci --ignore-scripts 2>&1 || npm install --ignore-scripts 2>&1 || true

# Install Python test dependencies
RUN uv pip install --system pytest pytest-asyncio

WORKDIR /workspace/playwright
