FROM node:22.13.1-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates \
        python3=3.11.2-1+b1 \
        python3-pip \
        python3-venv \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.17.1

RUN python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

WORKDIR /workspace

ARG REPO_URL=https://github.com/Effect-TS/effect.git
ARG BASE_COMMIT=4f2107548fa64c21a8643b7b0efcd556cd16d4b9

RUN git clone --filter=blob:none ${REPO_URL} effect && \
    cd effect && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/effect

ENV CI=1
RUN pnpm install --frozen-lockfile --ignore-scripts

RUN mkdir -p /logs/verifier
