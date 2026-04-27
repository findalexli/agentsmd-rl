FROM node:22.13.1-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace
RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin 33712058e2655dd50f9b2b511ab8d38c2bd5268a && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH="${PNPM_HOME}:${PATH}"

# Install all workspace deps offline-friendly (using the lockfile pinned at base commit)
RUN pnpm install --frozen-lockfile --prefer-offline

# Pre-build dependencies once so type-checking + tests don't have to rebuild
RUN pnpm --filter=effect --filter=@effect/platform --filter=@effect/rpc \
        --filter=@effect/sql --filter=@effect/workflow --filter=@effect/sql-sqlite-node \
        run build || true

RUN mkdir -p /logs/verifier

WORKDIR /workspace/effect
