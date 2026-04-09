FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends     git curl ca-certificates build-essential python3 python3-pip     && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/

# Configure git identity (needed for snapshot commit below)
RUN git config --global user.email "agent@example.com" &&     git config --global user.name "Agent"

# Clone React at the pre-fix commit
ARG BASE_COMMIT=3f0b9e61c467cd6e09cac6fb69f6e8f68cd3c5d7
RUN git clone https://github.com/facebook/react.git react && cd react &&     git fetch --depth=1 origin ${BASE_COMMIT} &&     git checkout ${BASE_COMMIT} &&     rm -rf .git &&     git init && git add -A && git commit -m "snapshot"

WORKDIR /workspace/react

# Install dependencies (minimal for testing)
RUN yarn install --frozen-lockfile

# Enable the feature flag for testing
RUN sed -i 's/enableInfiniteRenderLoopDetection: boolean = false/enableInfiniteRenderLoopDetection: boolean = true/' packages/shared/ReactFeatureFlags.js

# Create logs directory
RUN mkdir -p /logs/verifier

ENV NODE_ENV=development
ENV CI=true
