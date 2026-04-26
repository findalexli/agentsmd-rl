FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pytest-json-ctrf --break-system-packages

RUN git init /workspace/infisical && \
    cd /workspace/infisical && \
    git remote add origin https://github.com/Infisical/infisical.git && \
    git fetch --depth=1 origin e928398a0919194fc2efd855aaf6700424b507d9 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/infisical

RUN mkdir -p /logs/verifier

