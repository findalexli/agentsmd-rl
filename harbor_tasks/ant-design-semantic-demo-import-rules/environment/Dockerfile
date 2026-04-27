FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        grep \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4

WORKDIR /workspace

RUN git init ant-design \
    && cd ant-design \
    && git remote add origin https://github.com/ant-design/ant-design.git \
    && git -c protocol.version=2 fetch --depth=1 --filter=blob:none origin 11370a274afc12156f25d83f7f2e9af468feba1a \
    && git checkout FETCH_HEAD \
    && git config user.email "scaffold@example.com" \
    && git config user.name "scaffold"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
