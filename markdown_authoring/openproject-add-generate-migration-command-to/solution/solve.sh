#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openproject

# Idempotency guard
if grep -qF "bin/compose exec backend bundle exec rails db:migrate      # Run migrations" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -27,7 +27,7 @@ OpenProject supports two development setups: **Local** and **Docker**. Choose on
 ```bash
 bundle install                    # Install Ruby gems
 cd frontend && npm ci && cd ..   # Install Node packages
-bundle exec rake db:migrate      # Setup database
+bundle exec rails db:migrate      # Setup database
 bin/dev                          # Start all services (Rails, frontend, Good Job worker)
 # Access at http://localhost:3000
 ```
@@ -178,9 +178,10 @@ bin/setup              # Initial Rails setup
 bin/setup_dev          # Full dev environment setup
 
 # Database
-bundle exec rake db:migrate              # Run migrations
-bundle exec rake db:rollback             # Rollback last migration
-bundle exec rake db:seed                 # Seed sample data
+bundle exec rails g migration MigrationName  # Generate a migration
+bundle exec rails db:migrate                 # Run migrations
+bundle exec rails db:rollback                # Rollback last migration
+bundle exec rails db:seed                    # Seed sample data
 
 # Development
 bin/dev                                  # Start all services
@@ -189,7 +190,7 @@ bundle exec rails routes                 # List routes
 
 # Testing
 bundle exec rspec                        # Run RSpec tests
-bundle exec rake parallel:spec           # Parallel tests
+bundle exec rails parallel:spec          # Parallel tests
 cd frontend && npm test                  # Frontend tests
 
 # Linting
@@ -220,8 +221,8 @@ bin/compose logs -f backend              # Follow backend logs
 bin/compose ps                           # List running containers
 
 # Database
-bin/compose exec backend bundle exec rake db:migrate      # Run migrations
-bin/compose exec backend bundle exec rake db:seed         # Seed data
+bin/compose exec backend bundle exec rails db:migrate      # Run migrations
+bin/compose exec backend bundle exec rails db:seed         # Seed data
 
 # Direct docker-compose commands
 bin/compose up -d                        # Start services
PATCH

echo "Gold patch applied."
