FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/last30days-skill && \
    cd /workspace/last30days-skill && \
    git remote add origin https://github.com/mvanhorn/last30days-skill.git && \
    git fetch --depth=1 origin 1da9c601c35829688d4a65482fd46d010ca5e28f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/last30days-skill
