# Expose LLM Analytics Evaluation Summary as an MCP Tool

## Problem

Agents using PostHog's MCP integration cannot access the LLM evaluation results summariser. The backend endpoint `POST /api/environments/:id/llm_analytics/evaluation_summary/` is fully implemented with request/response serializers, `@extend_schema`, caching, rate limiting, and `is_ai_data_processing_approved` gating, but the corresponding MCP tool in the product's YAML config is currently disabled. There is also no skill document to help agents understand how to work with LLM evaluations.

## Expected Behavior

The evaluation summary MCP tool should be enabled and properly configured so agents can discover and invoke it. A skill document should be created for the evaluation workflow, following the existing patterns in `products/llm_analytics/skills/`.

## Files to Look At

- `products/llm_analytics/mcp/tools.yaml` — MCP tool definitions; the evaluation summary tool entry needs to be enabled with full metadata
- `products/llm_analytics/skills/` — existing skill documents for LLM analytics
- `products/llm_analytics/skills/README.md` — index of available skills
- `.agents/skills/implementing-mcp-tools/SKILL.md` — guide for MCP tool YAML configuration
- `.agents/skills/writing-skills/SKILL.md` — guide for writing skill documents
