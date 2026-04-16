FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm@10

WORKDIR /workspace

# Clone prisma repo (shallow)
RUN git clone --filter=blob:none --no-checkout https://github.com/prisma/prisma.git
WORKDIR /workspace/prisma
RUN git checkout 9fa295d70ff0497e0f0e4f06bdd5df76f6a9501a

# Install dependencies
RUN pnpm install --frozen-lockfile

WORKDIR /workspace
RUN mkdir -p /logs/verifier /tests

COPY test.sh /tests/test.sh
COPY test_outputs.py /tests/test_outputs.py
RUN chmod +x /tests/test.sh