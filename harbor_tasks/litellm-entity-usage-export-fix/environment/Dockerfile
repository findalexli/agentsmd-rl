FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 python3-pip git curl && \
  rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@9 2>/dev/null || true

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none https://github.com/BerriAI/litellm.git litellm_repo && \
  cd litellm_repo && \
  git fetch --depth=1 origin a5322c6efcd579c0ee8af7bae0f27fb07e350fd1 && \
  git checkout FETCH_HEAD && \
  mv ui/litellm-dashboard /workspace/litellm-dashboard && \
  rm -rf litellm_repo

WORKDIR /workspace/litellm-dashboard

# Install dependencies
RUN pnpm install 2>&1 | tail -5

# Install vitest for running tests
RUN pnpm add -D vitest @vitest/ui 2>&1 | tail -3

RUN mkdir -p /logs/verifier

# Install pytest system-wide (OK for container use)
RUN pip3 install pytest --break-system-packages -q

# Copy test harness (test_outputs.py and test.sh) into the container
COPY tests/ /workspace/litellm-dashboard/tests/