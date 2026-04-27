FROM node:22.22.0-trixie-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        make \
        g++ \
        openssh-client \
        openssl \
        unixodbc \
        freetds-bin \
        freetds-dev \
        unixodbc-dev \
        libc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /workspace
RUN git init /workspace/infisical && \
    cd /workspace/infisical && \
    git remote add origin https://github.com/Infisical/infisical.git && \
    git fetch --depth=1 origin d85308913a5fa4bf81d946dd2c69d9298242d90f && \
    git checkout FETCH_HEAD

WORKDIR /workspace/infisical/backend

# Disable the 7-day min-release-age policy: it forces npm to query an external
# registry endpoint that may not be reachable at build time.
RUN sed -i '/min-release-age/d' .npmrc 2>/dev/null || true

RUN npm install --no-audit --no-fund --prefer-offline=false 2>&1 | tail -50

RUN mkdir -p /logs/verifier
