FROM node:22.22.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        bash \
    && rm -rf /var/lib/apt/lists/*

# Pinned Python deps for the test runner.
RUN python3 -m pip install --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

ENV REPO_URL=https://github.com/apache/superset.git
ENV BASE_COMMIT=73c4240ba4780c0adafa68ffbd2c12f4c1673854

WORKDIR /workspace

RUN git clone --filter=blob:none ${REPO_URL} superset \
    && cd superset \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/superset/superset-frontend

# Install only frontend dependencies. CI=1 + --no-audit + --no-fund keep this
# quiet; --no-progress reduces log spam in Docker buildkit. The npm install
# is heavy but cached as a single layer.
RUN CI=1 npm ci --no-audit --no-fund --no-progress 2>&1 | tail -50

# Pre-warm the jest cache so the first test invocation is faster. This also
# surfaces any environment misconfigurations at build time.
RUN node -e "require.resolve('jest')" \
    && node -e "require.resolve('@testing-library/react-hooks')" \
    && node -e "require.resolve('redux-mock-store')"

WORKDIR /workspace/superset

RUN mkdir -p /logs/verifier
