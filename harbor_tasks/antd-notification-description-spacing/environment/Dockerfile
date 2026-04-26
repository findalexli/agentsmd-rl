FROM node:22-slim

# Install Python and required dependencies for pytest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the ant-design repository at base commit
# Using filter=blob:none for faster clone
RUN git init /workspace/ant-design && \
    cd /workspace/ant-design && \
    git remote add origin https://github.com/ant-design/ant-design.git && \
    git fetch --depth=1 origin 501436e5f45e533679f797ee0ee58e2a391e566d && \
    git checkout FETCH_HEAD

# Install dependencies (needed for tests)
WORKDIR /workspace/ant-design
RUN npm install --legacy-peer-deps

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Set back to workspace
WORKDIR /workspace
