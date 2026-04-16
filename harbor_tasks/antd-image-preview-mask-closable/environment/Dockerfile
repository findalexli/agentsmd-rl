FROM node:22-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Clone ant-design repo at the base commit
# Need full clone to get package-lock.json
RUN git clone --depth 1 --branch master https://github.com/ant-design/ant-design.git ant-design \
    && cd ant-design \
    && git fetch --depth=1 origin 3a6bde1947b2efdaf0c8964ef9a3022b483f33ae \
    && git checkout 3a6bde1947b2efdaf0c8964ef9a3022b483f33ae

# Install dependencies (without preparing husky hooks to avoid issues)
WORKDIR /workspace/ant-design
RUN npm install --ignore-scripts

# Install Python packages for testing
RUN pip3 install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for subsequent commands
WORKDIR /workspace/ant-design
