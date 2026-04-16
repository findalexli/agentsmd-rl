FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none --depth=1 https://github.com/continuedev/continue.git continue_repo
WORKDIR /workspace/continue_repo
RUN git fetch --depth=1 origin 2f52b46ec2c59bb3bf2f5df1c4630b001676e08d
RUN git checkout 2f52b46ec2c59bb3bf2f5df1c4630b001676e08d

# Install root workspace dependencies first
RUN npm install --ignore-scripts 2>&1 | tail -5

# Then install core devDependencies (where TypeScript and jest types are)
WORKDIR /workspace/continue_repo/core
RUN npm install --ignore-scripts 2>&1 | tail -5

# Back to root for running tests
WORKDIR /workspace/continue_repo

# Install pytest and test utilities
RUN pip install pytest taskforge --quiet

RUN mkdir -p /logs/verifier