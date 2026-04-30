FROM golang:1.23

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update &&     apt-get install -y --no-install-recommends         git curl ca-certificates python3 python3-pip python3-venv &&     rm -rf /var/lib/apt/lists/*

RUN git init /workspace/compose && \
    cd /workspace/compose && \
    git remote add origin https://github.com/docker/compose.git && \
    git fetch --depth=1 origin 27d9d506306e808965d99b70c1f59308dcabca13 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/compose

RUN mkdir -p /logs/verifier
