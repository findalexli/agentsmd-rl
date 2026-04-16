FROM node:22-slim

# Install Python and dependencies for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace
WORKDIR /workspace

# Clone the playwright repo at base commit
# Using depth=1 for faster clone since we only need the specific commit state
RUN git clone --depth=1 --filter=blob:none \
    https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git fetch --depth=1 origin 4df350b1c81b61ea471ff12767efd8e05f773377 && \
    git checkout 4df350b1c81b61ea471ff12767efd8e05f773377

# Install npm dependencies (needed for TypeScript compilation)
WORKDIR /workspace/playwright
RUN npm ci --ignore-scripts 2>&1 || npm install --ignore-scripts 2>&1 || true

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Set working directory for the tests
WORKDIR /workspace/playwright
