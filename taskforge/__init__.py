"""taskforge — Tooling for SWE benchmark task pipelines.

  scout:    PR scouting — filter candidates, split patches
  models:   Data models (EvalManifest, PRCandidate, Check, etc.)
  lint:     Static checks on test_outputs.py + solve.sh
  validate: Per-task status.json tracking + Docker oracle verdicts
  e2b:      E2B sandbox validation (parallel, cloud-based)
  judge:    LLM rubric judge for soft rules
  pipeline: Orchestrator — run stages via claude -p in parallel
  proxy:    LiteLLM proxy for routing to alternative models
"""

__version__ = "0.2.0"
