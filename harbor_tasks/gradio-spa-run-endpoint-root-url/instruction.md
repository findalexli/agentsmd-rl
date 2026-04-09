# Fix incorrect root URL when using /run/ endpoint

## Problem

When a Gradio app handles API requests through the `/run/{api_name}` endpoint (used by the SPA frontend and direct API consumers), the root URL computed for the response is incorrect. It includes the request route path (e.g., `http://localhost:7860/gradio_api/run/predict` instead of `http://localhost:7860`).

This causes file URLs in responses to be malformed — images, videos, and other media returned by cached examples or file-producing functions get 404 errors because the root URL has the route path baked in.

The `/api/{api_name}` endpoint is not affected because its path happens to match a hardcoded value used during URL construction.

## Expected Behavior

The root URL should always be the base server URL (e.g., `http://localhost:7860`) regardless of whether the request arrived via `/run/` or `/api/`. The route path should be stripped from the request URL when computing the root.

## Files to Look At

- `gradio/routes.py` — the `predict` endpoint handler, specifically where it calls `get_root_url`
- `gradio/route_utils.py` — the `get_root_url` and `get_request_origin` utility functions that compute the root URL
