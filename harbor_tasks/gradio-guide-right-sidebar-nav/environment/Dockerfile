FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO=gradio-app/gradio
ARG BASE_COMMIT=41e98f9468bcf322ed55d1470e31e7b4021d0480

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/${REPO}.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo