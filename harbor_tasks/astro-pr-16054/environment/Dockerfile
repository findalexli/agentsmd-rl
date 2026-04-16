FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm git curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo, then checkout the base commit
RUN git clone --depth=1 https://github.com/withastro/astro.git /workspace/astro && \
    cd /workspace/astro && \
    git fetch --depth=1 origin fa5bcded465bda258137f8017721ba15d54a9b4a && \
    git checkout fa5bcded465bda258137f8017721ba15d54a9b4a

WORKDIR /workspace/astro

# Install pnpm and only the deps needed for type-checking/linting
RUN npm install -g pnpm@9

# Install only astro package deps (not entire monorepo)
RUN pnpm install --no-frozen-lockfile --filter astro

# Create logs directory
RUN mkdir -p /logs/verifier
