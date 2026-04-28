FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/vibesec-skill && \
    cd /workspace/vibesec-skill && \
    git remote add origin https://github.com/BehiSecc/VibeSec-Skill.git && \
    git fetch --depth=1 origin 846c6790ae18ecc4798d0d1b9c6cbb7d818465a0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vibesec-skill
