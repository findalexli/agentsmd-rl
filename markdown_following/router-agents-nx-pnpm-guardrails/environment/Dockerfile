FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        pytest==8.3.4

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout 027dc0581750bc7db48600f438240ccb8b2bb1e8

WORKDIR /workspace/router

RUN mkdir -p /logs/verifier
