FROM python:3.12-slim

WORKDIR /workspace

# Install Node.js 20.x and git
RUN apt-get update && apt-get install -y curl git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository (shallow)
RUN git clone --filter=blob:none --depth=1 https://github.com/mantinedev/mantine.git

WORKDIR /workspace/mantine

# Checkout the base commit
RUN git fetch --depth=1 origin ae08675fc756cf40803ef7b365e18ed2fc0634ce \
    && git checkout ae08675fc756cf40803ef7b365e18ed2fc0634ce

# Install dependencies using Yarn (enable corepack to use version from packageManager)
RUN corepack enable \
    && corepack prepare yarn@4.10.3 --activate \
    && yarn install --immutable

# Install pytest and test dependencies
RUN pip install pytest==8.3.4 pytest-timeout==2.3.1

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]