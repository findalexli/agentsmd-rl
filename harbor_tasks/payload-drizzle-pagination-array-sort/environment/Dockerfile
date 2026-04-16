FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none https://github.com/payloadcms/payload.git

WORKDIR /workspace/payload

# Checkout base commit
RUN git checkout 6a9e36734119b6c8bc9633f9e212e0a29faa07df

# Install dependencies (pnpm version 10.x as required by repo engines)
RUN mkdir -p /tmp/pnpm-install && \
    npm install -g pnpm@10.33.0 --prefix /tmp/pnpm-install && \
    rm -rf /root/.npm

ENV PATH="/tmp/pnpm-install/bin:$PATH"

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier

COPY test.sh /tests/test.sh
RUN chmod +x /tests/test.sh

CMD ["bash", "/tests/test.sh"]