FROM node:20-slim

# Install necessary tools
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory to match expected repo location
WORKDIR /workspace/output

# Install TypeScript globally
RUN npm install -g typescript ts-node

# Copy package files from the repo
COPY repo/package*.json repo/tsconfig.json ./

# Install dependencies
RUN npm install

# Copy the rest of the code from repo
COPY repo/src ./src

# Default command
CMD ["bash"]
