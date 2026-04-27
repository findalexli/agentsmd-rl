FROM node:22.12.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Pinned pytest stack — used by the test harness, not by the repo itself.
RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

# Sparse-clone only the UI dashboard subtree we need to make this image small.
RUN git init /workspace/litellm && \
    cd /workspace/litellm && \
    git remote add origin https://github.com/BerriAI/litellm.git && \
    git fetch --depth=1 origin a292add9bd53a87e919a79aaeae8bbcb542cd033 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/litellm/ui/litellm-dashboard

# Install JS dependencies (uses package-lock.json from base commit for reproducibility).
RUN npm ci --no-audit --no-fund --no-progress

RUN mkdir -p /logs/verifier
