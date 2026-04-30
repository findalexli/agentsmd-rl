FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        patch \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pyyaml==6.0.2

ARG REPO_OWNER=cloudflare
ARG REPO_NAME=workers-sdk
ARG BASE_COMMIT=ad6799bd48742f0a589ed5867b269055015e4293

WORKDIR /workspace

RUN curl -sSL "https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/tar.gz/${BASE_COMMIT}" -o /tmp/repo.tgz \
    && tar -xzf /tmp/repo.tgz -C /workspace \
    && mv /workspace/${REPO_NAME}-${BASE_COMMIT} /workspace/${REPO_NAME} \
    && rm /tmp/repo.tgz

WORKDIR /workspace/workers-sdk

RUN git init -q \
    && git config user.email scaffold@local \
    && git config user.name scaffold \
    && git add -A \
    && git commit -q -m "base"

RUN mkdir -p /logs/verifier
