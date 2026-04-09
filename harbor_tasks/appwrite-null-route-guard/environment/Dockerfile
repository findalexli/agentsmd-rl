FROM php:8.3-cli

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    curl \
    libzip-dev \
    libonig-dev \
    libxml2-dev \
    libssl-dev \
    pkg-config \
    python3 \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions needed by the project
RUN docker-php-ext-install \
    mbstring \
    xml \
    zip

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /workspace

# Clone the appwrite repository at the base commit
RUN git clone https://github.com/appwrite/appwrite.git && \
    cd appwrite && \
    git checkout 951a96ae01bceaabe6e2fb936686b7953209ce19

# Set working directory to the repo
WORKDIR /workspace/appwrite

# Install composer dependencies (with --ignore-platform-req to handle missing extensions)
RUN composer install --no-interaction --optimize-autoloader --ignore-platform-req=ext-swoole --ignore-platform-req=ext-mongodb --ignore-platform-req=ext-redis --ignore-platform-req=ext-pdo_mysql --ignore-platform-req=ext-pdo_pgsql --ignore-platform-req=ext-curl --ignore-platform-req=ext-imagick 2>/dev/null || true

# Set working directory back to /workspace for test execution
WORKDIR /workspace

# Create entrypoint script to symlink test file at runtime
RUN echo '#!/bin/bash\nln -sf /tests/test_outputs.py /workspace/test_outputs.py 2>/dev/null || true\nexec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
