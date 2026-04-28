FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    python3 \
    python3-pip \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.18.0 LTS (pinned version)
RUN curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz \
    | tar -xJ -C /usr/local --strip-components=1 \
    && node --version && npm --version

# Install TypeScript globally
RUN npm install -g typescript

RUN pip install pytest --quiet

WORKDIR /workspace

# Clone the repo with base commit reachable
RUN git clone --filter=blob:none --no-single-branch https://github.com/effect-ts/effect.git \
    && cd effect && git fetch --depth=1 origin 590dbfc942277fe2be68cf9a81b40335c6640821 \
    && git checkout 590dbfc942277fe2be68cf9a81b40335c6640821

RUN mkdir -p /logs/verifier
