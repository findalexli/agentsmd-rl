FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

RUN npm install -g typescript@5.7.2

WORKDIR /workspace

ARG REPO_URL=https://github.com/microsoft/playwright.git
ARG BASE_COMMIT=4df350b1c81b61ea471ff12767efd8e05f773377

RUN git clone --filter=blob:none --no-checkout "${REPO_URL}" playwright \
    && cd playwright \
    && git fetch --depth=1 origin "${BASE_COMMIT}" \
    && git checkout FETCH_HEAD \
    && git config user.email "task@example.com" \
    && git config user.name "task"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/playwright
