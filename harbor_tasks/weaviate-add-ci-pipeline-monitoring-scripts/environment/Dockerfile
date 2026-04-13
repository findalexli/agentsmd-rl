FROM node:20-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace/sample_repo

# Copy the repo
COPY sample_repo/ /workspace/sample_repo/

# Install npm dependencies
RUN npm install
