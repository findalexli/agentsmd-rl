# Webpack Memory Optimization: TypeScript Checker Control

## Problem

The webpack development server in `superset-frontend` consumes excessive memory (7-8GB heap) during local development, particularly when running in Docker environments.

One major contributor to this memory usage is the `ForkTsCheckerWebpackPlugin` which runs TypeScript type checking. While type checking is valuable, it adds ~2-3GB to memory consumption. For development workflows where type errors are caught by pre-commit hooks and CI, this overhead is unnecessary.

## Task

Implement an environment variable `DISABLE_TS_CHECKER` that allows developers to optionally skip the TypeScript checker plugin during webpack builds.

### Requirements

1. **Boolean parsing**: The flag should only be considered "enabled" (meaning the checker is disabled) when the value is exactly `"true"` or `"1"` (case insensitive). Any other value including `"false"`, `"0"`, or empty string should keep the checker enabled.

2. **Development mode only**: The TypeScript checker plugin is only added in development mode. The disable flag should respect this - it should only affect dev mode behavior.

3. **CSS sourceMap optimization**: Additionally, CSS source maps should be disabled in development mode to further reduce memory usage (they're mainly useful for production debugging).

4. **Watch pattern optimization**: The webpack watcher should ignore additional non-essential file patterns to reduce file handle usage:
   - `**/.temp_cache`
   - `**/coverage`
   - `**/*.test.*`
   - `**/*.stories.*`
   - `**/cypress-base`
   - `**/*.geojson`

5. **Docker environment support**: The `docker-compose-light.yml` file should set this flag to `true` by default for lighter development containers. The flask reloader should also exclude the frontend directory from its watch patterns.

## Files to Modify

- `superset-frontend/webpack.config.js` - Main webpack configuration
- `docker-compose-light.yml` - Docker compose for lightweight development
- `docker/docker-bootstrap.sh` - Flask server startup script
