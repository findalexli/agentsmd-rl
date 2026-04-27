FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/terraform-skill && \
    cd /workspace/terraform-skill && \
    git remote add origin https://github.com/antonbabenko/terraform-skill.git && \
    git fetch --depth=1 origin fd3aab0efa67b84dd3798ad25510f480a0dcf3f9 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/terraform-skill
