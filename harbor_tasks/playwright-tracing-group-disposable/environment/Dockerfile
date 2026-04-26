FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV PLAYWRIGHT_BROWSERS_PATH=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /workspace
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 1ed53ac99ec225a5fc0aacb762a18e3195c61a6c && \
    git checkout FETCH_HEAD

WORKDIR /workspace/playwright

RUN npm ci --ignore-scripts --no-audit --no-fund --loglevel=error

RUN node utils/build/build.js --disable-install 2>&1 | tail -5

RUN mkdir -p /logs/verifier

CMD ["bash"]
