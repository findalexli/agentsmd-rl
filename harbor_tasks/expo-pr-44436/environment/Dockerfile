FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ruby ruby-dev build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone expo repo at base commit, keep full structure for patch compatibility
RUN git clone --depth=1 https://github.com/expo/expo.git && \
    cd expo && \
    git fetch --depth=1 origin 68af44553b6f53b6329c59a42dc586b1d83bf2d6 && \
    git checkout 68af44553b6f53b6329c59a42dc586b1d83bf2d6

# Symlink the package to the expected path for task validation
RUN ln -s /workspace/expo/packages/expo-modules-autolinking /workspace/expo-modules-autolinking

RUN mkdir -p /logs/verifier

ENV RUBYLIB=/workspace/expo-modules-autolinking/scripts/ios