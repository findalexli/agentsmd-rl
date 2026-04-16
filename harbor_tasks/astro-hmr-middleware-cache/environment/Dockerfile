FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the Astro repo at base commit
# Using depth=500 to get enough history while keeping it reasonably fast
RUN git clone --depth=500 --branch main https://github.com/withastro/astro.git /workspace/astro && \
    cd /workspace/astro && \
    git checkout fa5bcded465bda258137f8017721ba15d54a9b4a

WORKDIR /workspace/astro

# Install pnpm (required for Astro monorepo)
RUN npm install -g pnpm

# Install dependencies for the astro package only
# This is needed for TypeScript checking
RUN pnpm install --frozen-lockfile --ignore-scripts || \
    pnpm install --ignore-scripts

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Keep container running
CMD ["bash"]
