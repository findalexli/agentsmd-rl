FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/gemini-skills && \
    cd /workspace/gemini-skills && \
    git remote add origin https://github.com/google-gemini/gemini-skills.git && \
    git fetch --depth=1 origin e838c6e8f406b0f06e940bd05367e57b166e24f7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gemini-skills
