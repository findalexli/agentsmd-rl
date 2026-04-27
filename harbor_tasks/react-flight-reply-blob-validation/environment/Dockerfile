FROM node:20.19.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        bash \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH="/opt/venv/bin:${PATH}"

ENV REACT_REPO=/workspace/react
ENV BASE_COMMIT=c80a07509582daadf275f36ffe7a88c3b12e9db4

RUN git clone --filter=blob:none https://github.com/facebook/react.git ${REACT_REPO} \
    && cd ${REACT_REPO} \
    && git checkout ${BASE_COMMIT} \
    && git config user.email "task@example.com" \
    && git config user.name "Task Runner"

WORKDIR ${REACT_REPO}

RUN yarn install --frozen-lockfile --network-timeout 600000 \
    && yarn cache clean

RUN mkdir -p /logs/verifier

WORKDIR ${REACT_REPO}
