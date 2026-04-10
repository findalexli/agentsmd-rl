FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone expo at base commit (shallow snapshot for speed)
RUN git init /workspace/expo && \
    cd /workspace/expo && \
    git remote add origin https://github.com/expo/expo.git && \
    git fetch --depth=1 origin e7f9f0359afa2414576dd57c9166272e3b64c5df && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/expo

# Install @babel/core and other deps in a temp location outside workspace,
# then copy to the babel-preset-expo directory for testing
RUN mkdir -p /tmp/babel-install && cd /tmp/babel-install && \
    echo '{"name": "temp", "version": "1.0.0"}' > package.json && \
    npm install @babel/core@"^7.26.0" @babel/generator @babel/helper-module-imports resolve-from \
        @babel/plugin-proposal-decorators @babel/plugin-proposal-export-default-from \
        @babel/plugin-syntax-export-default-from @babel/plugin-transform-class-static-block \
        @babel/plugin-transform-export-namespace-from @babel/plugin-transform-flow-strip-types \
        @babel/plugin-transform-modules-commonjs @babel/plugin-transform-object-rest-spread \
        @babel/plugin-transform-parameters @babel/plugin-transform-private-methods \
        @babel/plugin-transform-private-property-in-object @babel/plugin-transform-runtime \
        @babel/preset-react @babel/preset-typescript debug 2>&1 | tail -3 && \
    mkdir -p /workspace/expo/packages/babel-preset-expo/node_modules && \
    cp -r node_modules/* /workspace/expo/packages/babel-preset-expo/node_modules/

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
