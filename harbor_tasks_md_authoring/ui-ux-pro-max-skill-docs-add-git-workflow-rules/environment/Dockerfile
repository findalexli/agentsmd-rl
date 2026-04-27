FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ui-ux-pro-max-skill && \
    cd /workspace/ui-ux-pro-max-skill && \
    git remote add origin https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git && \
    git fetch --depth=1 origin 2e7acbf50f8ea257e1d4e0629baf87bf5e6c71b3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ui-ux-pro-max-skill
