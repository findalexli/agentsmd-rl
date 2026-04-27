FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates=20230311+deb12u1 \
        python3=3.11.2-1+b1 \
        python3-pip=23.0.1+dfsg-1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

RUN npm install -g tsx@4.19.2

WORKDIR /workspace

ARG REPO_URL=https://github.com/apache/superset.git
ARG BASE_COMMIT=1462ac92823bfb53d48b67604d8ba813f69738e0

RUN git clone --filter=blob:none --no-checkout "$REPO_URL" superset \
 && cd superset \
 && git fetch --depth 1 origin "$BASE_COMMIT" \
 && git checkout "$BASE_COMMIT"

WORKDIR /workspace/superset

RUN mkdir -p /logs/verifier

CMD ["bash"]
