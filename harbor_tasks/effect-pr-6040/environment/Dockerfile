FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pytest --break-system-packages --quiet

RUN npm install -g pnpm@10.4.0

WORKDIR /workspace

# Clone at base commit (before the fix)
RUN git clone --filter=blob:none --depth=1 https://github.com/effect-ts/effect.git
WORKDIR /workspace/effect
RUN git fetch --filter=blob:none origin 904e055143ad74b1e4cd25429f44e7a3e86db5dc
RUN git checkout 904e055143ad74b1e4cd25429f44e7a3e86db5dc

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier

RUN chmod +x /tests/test.sh

WORKDIR /workspace/effect