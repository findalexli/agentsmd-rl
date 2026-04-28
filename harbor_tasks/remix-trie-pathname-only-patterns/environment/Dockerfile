FROM node:24-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
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

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/remix-run/remix.git \
    && cd remix \
    && git checkout 3aa3d939d558aac03bfb0f3796bb7d6d4aacfa70

WORKDIR /workspace/remix

RUN corepack enable && pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
