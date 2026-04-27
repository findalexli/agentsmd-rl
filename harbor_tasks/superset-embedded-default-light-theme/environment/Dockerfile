FROM node:22.22.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        libpython3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1

ENV REPO_DIR=/workspace/superset
ENV BASE_COMMIT=dcb414aa0640498e55735716ecb0d94e25bcc5c4

RUN mkdir -p ${REPO_DIR} \
 && cd ${REPO_DIR} \
 && git init -q \
 && git remote add origin https://github.com/apache/superset.git \
 && git config core.sparseCheckout true \
 && echo "superset-frontend/" > .git/info/sparse-checkout \
 && git -c protocol.version=2 fetch --depth 1 --filter=blob:none origin ${BASE_COMMIT} \
 && git checkout FETCH_HEAD \
 && git config user.email "task@local" \
 && git config user.name  "task"

WORKDIR ${REPO_DIR}/superset-frontend

RUN npm ci --no-audit --no-fund --prefer-offline --legacy-peer-deps --ignore-scripts 2>&1 | tail -20

RUN mkdir -p /logs/verifier

CMD ["bash"]
