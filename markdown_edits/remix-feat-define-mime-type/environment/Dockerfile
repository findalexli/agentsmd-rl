FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 9c05f82591c422ffc958bd61deb1b29c181ae225 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# No pnpm install needed — generated files are committed, tests run from source
# using node --experimental-strip-types

RUN mkdir -p /logs/verifier
