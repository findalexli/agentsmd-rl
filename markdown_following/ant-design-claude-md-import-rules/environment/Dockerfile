FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.6

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design \
 && cd ant-design \
 && git checkout 1f41cc73e855b332d81fc52cd84f1dddad6676a6

# Install remark linter for CI parity (scoped to the repo so plugins resolve)
RUN cd ant-design \
    && npm install --no-save --no-package-lock \
        remark-cli@12.0.1 \
        remark-preset-lint-recommended@7.0.1 \
        remark-lint-no-undefined-references@5.0.2 \
    && rm -rf /root/.npm/_cacache

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
