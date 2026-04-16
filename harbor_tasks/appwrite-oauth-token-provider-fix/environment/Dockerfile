FROM php:8.3-cli

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --depth 100 https://github.com/appwrite/appwrite.git && \
    cd appwrite && \
    git fetch --depth 1 origin 6e59e1307d69b29f458bceec835c051c54dd76a9 && \
    git checkout 6e59e1307d69b29f458bceec835c051c54dd76a9

# Install PHP dependencies (without dev dependencies to save time)
WORKDIR /workspace/appwrite
RUN composer install --no-dev --no-interaction --optimize-autoloader 2>/dev/null || true

# Set up Python environment for tests
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install pytest requests
ENV PATH="/opt/venv/bin:$PATH"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/appwrite
