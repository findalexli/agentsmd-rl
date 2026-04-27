FROM oven/bun:1.3.13-debian

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
    pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone opencode at the base commit (parent of PR #23227 merge commit).
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode \
  && cd /workspace/opencode \
  && git checkout 1dd257b76a98a159f763ec009bf061e6bd4ae718

# A separate sandbox containing only the dependencies the keybinds module
# actually needs (effect + zod). The probe imports the file under
# /workspace/opencode/packages/opencode/src/config/keybinds.ts via a thin
# shim so that we don't pay the full opencode bun-install cost in the image
# while still testing the agent-edited file in-place.
WORKDIR /workspace/sandbox
RUN echo '{"name":"sandbox","type":"module","dependencies":{"effect":"4.0.0-beta.48","zod":"4.1.8"}}' > package.json \
  && bun install \
  && bun --version

# Expose the sandbox's node_modules to the cloned repo so bun can resolve
# `effect` and `zod` for the existing util/effect-zod.test.ts when we run it
# from packages/opencode (the file imports `../../src/util/effect-zod`,
# walks up from there for node_modules, and otherwise wouldn't find the
# packages without a full opencode workspace install).
RUN ln -s /workspace/sandbox/node_modules /workspace/opencode/node_modules

WORKDIR /workspace
