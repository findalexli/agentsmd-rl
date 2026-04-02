FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/react

# Clone React repo at base commit (parent of merge commit 8b6b11f7)
# Base commit: ab18f33d46171ed1963ae1ac955c5110bb1eb199
ENV REACT_COMMIT=ab18f33d46171ed1963ae1ac955c5110bb1eb199
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin ${REACT_COMMIT} && \
    git checkout ${REACT_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Install compiler dependencies
WORKDIR /workspace/react/compiler
RUN npm install --legacy-peer-deps || yarn install --frozen-lockfile

# Configure git user in case build needs it
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory to compiler package
WORKDIR /workspace/react/compiler/packages/babel-plugin-react-compiler
