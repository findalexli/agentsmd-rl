FROM node:22.12.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

# Sparse-checkout only the dashboard (the change is UI-only).
RUN git init /workspace/litellm && \
    cd /workspace/litellm && \
    git remote add origin https://github.com/BerriAI/litellm.git && \
    git fetch --depth=1 origin 50a52f62e3ad8c903068fdd580b98eb7adc30918 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/litellm/ui/litellm-dashboard

# Install dashboard deps.  npm ci uses the committed package-lock.json so the
# installed versions are deterministic.
RUN npm ci --no-audit --no-fund --prefer-offline --loglevel=error

RUN mkdir -p /logs/verifier

WORKDIR /workspace/litellm
