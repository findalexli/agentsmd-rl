FROM node:22-slim

# Install git and Python for pytest
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create working directory
WORKDIR /workspace

# Clone the OpenHands repo at the base commit
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout a198599d917fca47c467715b43858fc30f8082d4

# Set working directory to frontend
WORKDIR /workspace/OpenHands/frontend

# Install frontend dependencies
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variables for testing
ENV VITE_MOCK_API=true
ENV CI=true
