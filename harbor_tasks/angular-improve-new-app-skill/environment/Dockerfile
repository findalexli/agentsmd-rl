FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        grep \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.7

WORKDIR /workspace

# Sparse-checkout only the path the PR touches (the angular monorepo is huge,
# and this is a markdown_authoring task — the rest of the tree is unused).
RUN git clone --filter=blob:none --no-checkout \
        https://github.com/angular/angular.git /workspace/angular
WORKDIR /workspace/angular
RUN git sparse-checkout init --cone \
    && git sparse-checkout set skills/dev-skills/angular-new-app \
    && git checkout 8fa66173523bb275d33de4bd43ce23947812922e

RUN mkdir -p /logs/verifier

WORKDIR /workspace
