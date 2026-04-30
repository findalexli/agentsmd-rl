FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    unzip \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-ctrf==0.4.1

RUN curl -fsSL https://nodejs.org/dist/v22.13.0/node-v22.13.0-linux-x64.tar.xz \
    | tar -xJ -C /opt && \
    ln -s /opt/node-v22.13.0-linux-x64/bin/node /usr/local/bin/node && \
    ln -s /opt/node-v22.13.0-linux-x64/bin/npm /usr/local/bin/npm && \
    ln -s /opt/node-v22.13.0-linux-x64/bin/npx /usr/local/bin/npx

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset && \
    cd superset && \
    git checkout 5cff6578121d1e813bb454b970fea05b720aeb6f

RUN mkdir -p /test_harness && cd /test_harness && \
    npm init -y >/dev/null && \
    npm install --no-audit --no-fund --loglevel=error \
        react@17.0.2 \
        react-dom@17.0.2 \
        @visx/responsive@3.12.0 \
        jsdom@26.0.0 \
        esbuild@0.25.0

COPY harness/ /test_harness/

RUN mkdir -p /logs/verifier
