FROM php:8.3-cli

# Install system dependencies
RUN apt-get update && apt-get install -y     git     unzip     libzip-dev     libonig-dev     libxml2-dev     libpq-dev     libmongoc-1.0-0     libssl-dev     pkg-config     && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install zip mbstring xml pdo pdo_mysql pdo_pgsql

# Install MongoDB extension
RUN pecl install mongodb && docker-php-ext-enable mongodb

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Install Python for test runner
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none --depth=100 https://github.com/appwrite/appwrite.git appwrite &&     cd appwrite &&     git checkout 4e10cabec0bf504daffb1bc53ad86bdf6f2cc727

# Install PHP dependencies including dev dependencies (for lint/analyze tools)
RUN cd /workspace/appwrite &&     if [ -f composer.json ]; then         composer install --optimize-autoloader --ignore-platform-reqs;     fi

ENV REPO_PATH=/workspace/appwrite
