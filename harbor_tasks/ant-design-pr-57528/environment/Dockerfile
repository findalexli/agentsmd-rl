# Dockerfile for ant-design popconfirm icon semantic task
FROM node:22-slim

# Install git, python3, and pytest (needed by test runner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design \
    && cd ant-design \
    && git checkout 611be598bdba1665aebd09bfedebb7001926a5c1

WORKDIR /workspace/ant-design

# Install dependencies
RUN npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set default command
CMD ["bash"]
