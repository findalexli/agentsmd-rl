FROM node:22.22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_OPTIONS="--max-old-space-size=8192"

RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.39.5-0+deb12u2 \
    ca-certificates \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1

WORKDIR /workspace
ARG REPO_URL=https://github.com/apache/superset.git
ARG BASE_COMMIT=fdcb942f3c7c33cac49032ab748eb3a68eaa8bfa
RUN git clone --filter=blob:none "$REPO_URL" superset && \
    cd superset && \
    git checkout "$BASE_COMMIT"

WORKDIR /workspace/superset/superset-frontend

RUN npm ci --prefer-offline --no-audit --no-fund --ignore-scripts 2>&1 | tail -20

RUN mkdir -p /logs/verifier
