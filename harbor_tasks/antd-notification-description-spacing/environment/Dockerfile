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
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git /workspace/ant-design \
    && cd /workspace/ant-design \
    && git checkout 501436e5f45e533679f797ee0ee58e2a391e566d

# Install dependencies (needed for tests)
WORKDIR /workspace/ant-design
RUN npm install

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Set back to workspace
WORKDIR /workspace
