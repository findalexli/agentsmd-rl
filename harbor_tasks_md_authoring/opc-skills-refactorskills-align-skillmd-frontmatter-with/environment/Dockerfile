FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/opc-skills && \
    cd /workspace/opc-skills && \
    git remote add origin https://github.com/ReScienceLab/opc-skills.git && \
    git fetch --depth=1 origin 515e1f5e5a5261467c1e526dc20829258c090ebf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opc-skills
