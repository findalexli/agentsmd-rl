FROM node:22-bookworm

# Install Python3 and git for pytest harness and repo clone
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest for the test harness
RUN pip3 install pytest --break-system-packages

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.28.0 --activate

# Clone repo with blob filter for speed
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router
RUN git checkout 5c5a4359e837b4f4aa424b047709008e40d69497

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the required packages for the e2e test
RUN pnpm nx run-many --target=build --projects=@tanstack/history,@tanstack/router-core,@tanstack/react-router,@tanstack/router-devtools-core,@tanstack/react-router-devtools,@tanstack/router-generator,@tanstack/virtual-file-routes,@tanstack/router-plugin,@tanstack/zod-adapter --skip-nx-cache

# Create logs directory
RUN mkdir -p /logs/verifier
