FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/julia-agent-skills && \
    cd /workspace/julia-agent-skills && \
    git remote add origin https://github.com/JuliaGenAI/julia-agent-skills.git && \
    git fetch --depth=1 origin 864698b9ff5de8d33ae62277a4fe098789a60518 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/julia-agent-skills
