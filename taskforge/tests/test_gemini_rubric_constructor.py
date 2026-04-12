"""Tests for gemini_rubric_constructor: structured output schemas, stamping, Kimi loop."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import yaml

from taskforge.gemini_rubric_constructor import (
    RUBRIC_RESPONSE_SCHEMA,
    COMBINED_RUBRIC_QUALITY_SCHEMA,
    KIMI_VALIDATION_SCHEMA,
    _POSITIVE_RUBRIC_SCHEMA,
    _NEGATIVE_RUBRIC_SCHEMA,
    call_gemini,
    _extract_json_from_text,
    _to_rubric_dict,
    _to_distractor_dict,
    _apply_kimi_verdicts,
    _build_gemini_reevaluation_prompt,
    stamp_rubrics_to_manifest,
    build_rubric_prompt,
    build_kimi_validation_prompt,
    construct_rubrics,
    construct_rubrics_with_kimi,
    run_rubric_quality_loop,
)


# ── Schema validation tests ─────────────────────────────────────────────────

class TestSchemas(unittest.TestCase):
    """Verify structured output schemas are well-formed."""

    def test_rubric_response_schema_has_required_fields(self):
        assert RUBRIC_RESPONSE_SCHEMA["type"] == "object"
        assert "positive_rubrics" in RUBRIC_RESPONSE_SCHEMA["properties"]
        assert "negative_rubrics" in RUBRIC_RESPONSE_SCHEMA["properties"]
        assert "positive_rubrics" in RUBRIC_RESPONSE_SCHEMA["required"]
        assert "negative_rubrics" in RUBRIC_RESPONSE_SCHEMA["required"]

    def test_positive_rubric_schema_property_ordering(self):
        """Reasoning (evidence) must come before verdict (rule)."""
        order = _POSITIVE_RUBRIC_SCHEMA["propertyOrdering"]
        assert order.index("evidence_in_gold") < order.index("rule")
        assert order.index("source_file") < order.index("rule")

    def test_negative_rubric_schema_property_ordering(self):
        """Reasoning (why_distracting) must come before classification."""
        order = _NEGATIVE_RUBRIC_SCHEMA["propertyOrdering"]
        assert order.index("why_distracting") < order.index("collision_type")
        assert order.index("why_distracting") < order.index("rule")

    def test_negative_rubric_collision_type_enum(self):
        enum_vals = _NEGATIVE_RUBRIC_SCHEMA["properties"]["collision_type"]["enum"]
        expected = {"rule_conflict", "scope_ambiguity", "meta_confusion",
                    "architecture_boundary", "would_cause_bug"}
        assert set(enum_vals) == expected

    def test_negative_rubric_severity_enum(self):
        enum_vals = _NEGATIVE_RUBRIC_SCHEMA["properties"]["severity"]["enum"]
        assert set(enum_vals) == {"high", "medium", "low"}

    def test_positive_rubric_category_enum(self):
        enum_vals = _POSITIVE_RUBRIC_SCHEMA["properties"]["category"]["enum"]
        expected = {"naming", "style", "architecture", "testing", "documentation", "tooling"}
        assert set(enum_vals) == expected

    def test_kimi_validation_schema_verdict_enum(self):
        verdict_enum = KIMI_VALIDATION_SCHEMA["properties"]["rubric_verdicts"]["items"]["properties"]["verdict"]["enum"]
        assert set(verdict_enum) == {"confirmed", "revised", "rejected"}

    def test_kimi_validation_schema_has_task_verdict(self):
        """Schema must include task_verdict for abandon autonomy."""
        assert "task_verdict" in KIMI_VALIDATION_SCHEMA["properties"]
        enum_vals = KIMI_VALIDATION_SCHEMA["properties"]["task_verdict"]["enum"]
        assert set(enum_vals) == {"continue", "abandon"}
        assert "task_verdict" in KIMI_VALIDATION_SCHEMA["required"]

    def test_kimi_validation_reasoning_before_verdict(self):
        order = KIMI_VALIDATION_SCHEMA["properties"]["rubric_verdicts"]["items"]["propertyOrdering"]
        assert order.index("reasoning") < order.index("verdict")

    def test_top_level_property_ordering(self):
        """positive_rubrics before negative_rubrics at top level."""
        order = RUBRIC_RESPONSE_SCHEMA["propertyOrdering"]
        assert order.index("positive_rubrics") < order.index("negative_rubrics")


# ── JSON extraction tests ────────────────────────────────────────────────────

class TestExtractJson(unittest.TestCase):

    def test_plain_json(self):
        result = _extract_json_from_text('{"a": 1}')
        assert result == {"a": 1}

    def test_json_in_markdown_fence(self):
        text = 'Some text\n```json\n{"a": 1}\n```\nMore text'
        result = _extract_json_from_text(text)
        assert result == {"a": 1}

    def test_json_in_generic_fence(self):
        text = 'Blah\n```\n{"b": 2}\n```'
        result = _extract_json_from_text(text)
        assert result == {"b": 2}

    def test_json_with_prefix_text(self):
        text = 'Here is the result: {"c": 3}'
        result = _extract_json_from_text(text)
        assert result == {"c": 3}

    def test_unparseable_returns_error(self):
        result = _extract_json_from_text("not json at all")
        assert "error" in result

    def test_json_array(self):
        result = _extract_json_from_text('[{"a": 1}]')
        assert result == [{"a": 1}]


# ── Conversion to canonical dicts ────────────────────────────────────────────

class TestCanonicalConversion(unittest.TestCase):

    def test_to_rubric_dict_full(self):
        pr = {
            "rule": "Use const over let",
            "source_file": "AGENTS.md",
            "source_lines": "28-32",
            "evidence_in_gold": "Gold uses const for all declarations",
            "category": "style",
        }
        d = _to_rubric_dict(pr)
        assert d["rule"] == "Use const over let"
        assert d["source"] == {"path": "AGENTS.md", "lines": "28-32"}
        assert d["evidence"] == "Gold uses const for all declarations"
        assert d["category"] == "style"

    def test_to_rubric_dict_minimal(self):
        pr = {"rule": "Test rule"}
        d = _to_rubric_dict(pr)
        assert d == {"rule": "Test rule"}
        assert "source" not in d
        assert "evidence" not in d

    def test_to_distractor_dict_full(self):
        nr = {
            "rule": "Run pnpm build",
            "source_file": "CLAUDE.md",
            "source_lines": "60-65",
            "collision_type": "scope_ambiguity",
            "why_distracting": "Builds entire monorepo",
            "severity": "high",
        }
        d = _to_distractor_dict(nr)
        assert d["rule"] == "Run pnpm build"
        assert d["source"] == {"path": "CLAUDE.md", "lines": "60-65"}
        assert d["collision_type"] == "scope_ambiguity"
        assert d["severity"] == "high"

    def test_to_distractor_dict_defaults(self):
        nr = {"rule": "Some rule"}
        d = _to_distractor_dict(nr)
        assert d["severity"] == "medium"  # default
        assert d["collision_type"] == ""
        assert "source" not in d

    def test_evidence_truncated_at_200(self):
        pr = {
            "rule": "x",
            "source_file": "f.md",
            "evidence_in_gold": "A" * 300,
        }
        d = _to_rubric_dict(pr)
        assert len(d["evidence"]) == 200


# ── Stamp to manifest tests ─────────────────────────────────────────────────

class TestStampManifest(unittest.TestCase):

    def setUp(self):
        self.task_dir = Path("/tmp/test_stamp_task")
        self.task_dir.mkdir(parents=True, exist_ok=True)
        # Create a minimal manifest
        manifest = {
            "version": "2.0",
            "source": {"repo": "test/repo", "pr": 1, "base_commit": "abc"},
            "rubric": [
                {"rule": "Existing rule", "source": {"path": "CLAUDE.md", "lines": "1"}},
            ],
        }
        (self.task_dir / "eval_manifest.yaml").write_text(yaml.dump(manifest))

    def test_merges_positive_rubrics(self):
        """New rubrics are merged, not replaced."""
        result = {
            "positive_rubrics": [
                {"rule": "New rule", "source_file": "AGENTS.md", "source_lines": "5"},
            ],
            "negative_rubrics": [],
        }
        stamp_rubrics_to_manifest(self.task_dir, result)
        m = yaml.safe_load((self.task_dir / "eval_manifest.yaml").read_text())
        rules = [r["rule"] for r in m["rubric"]]
        assert "Existing rule" in rules
        assert "New rule" in rules
        assert len(m["rubric"]) == 2

    def test_deduplicates_rubrics(self):
        """Same rule text is not added twice."""
        result = {
            "positive_rubrics": [
                {"rule": "Existing rule", "source_file": "CLAUDE.md"},
            ],
            "negative_rubrics": [],
        }
        stamp_rubrics_to_manifest(self.task_dir, result)
        m = yaml.safe_load((self.task_dir / "eval_manifest.yaml").read_text())
        assert len(m["rubric"]) == 1

    def test_stamps_distractors(self):
        result = {
            "positive_rubrics": [],
            "negative_rubrics": [
                {
                    "rule": "Run all tests",
                    "source_file": "CLAUDE.md",
                    "source_lines": "10",
                    "collision_type": "scope_ambiguity",
                    "why_distracting": "Would build entire project",
                    "severity": "medium",
                },
            ],
        }
        stamp_rubrics_to_manifest(self.task_dir, result)
        m = yaml.safe_load((self.task_dir / "eval_manifest.yaml").read_text())
        assert len(m["distractors"]) == 1
        d = m["distractors"][0]
        assert d["collision_type"] == "scope_ambiguity"
        assert d["severity"] == "medium"
        assert "source" in d
        # Verify only canonical fields
        valid_keys = {"rule", "source", "collision_type", "why_distracting", "severity"}
        assert set(d.keys()) <= valid_keys

    def test_stamps_hierarchy_analysis(self):
        result = {
            "positive_rubrics": [],
            "negative_rubrics": [],
            "hierarchy_analysis": "Root CLAUDE.md overrides child.",
        }
        stamp_rubrics_to_manifest(self.task_dir, result)
        m = yaml.safe_load((self.task_dir / "eval_manifest.yaml").read_text())
        assert m["hierarchy_analysis"] == "Root CLAUDE.md overrides child."

    def test_no_manifest_is_noop(self):
        """stamp_rubrics_to_manifest does nothing if no manifest."""
        empty_dir = Path("/tmp/test_stamp_empty")
        empty_dir.mkdir(parents=True, exist_ok=True)
        stamp_rubrics_to_manifest(empty_dir, {"positive_rubrics": [{"rule": "x"}]})
        assert not (empty_dir / "eval_manifest.yaml").exists()

    def test_distractor_canonical_fields_only(self):
        """No stray fields leak into distractors."""
        result = {
            "positive_rubrics": [],
            "negative_rubrics": [
                {
                    "rule": "R",
                    "source_file": "X.md",
                    "source_lines": "1",
                    "collision_type": "meta_confusion",
                    "why_distracting": "reasons",
                    "severity": "low",
                    "extra_field": "should not appear",
                },
            ],
        }
        stamp_rubrics_to_manifest(self.task_dir, result)
        m = yaml.safe_load((self.task_dir / "eval_manifest.yaml").read_text())
        d = m["distractors"][0]
        assert "extra_field" not in d


# ── call_gemini with structured output ───────────────────────────────────────

class TestCallGeminiStructured(unittest.TestCase):

    @patch("urllib.request.urlopen")
    def test_structured_output_adds_schema_to_request(self, mock_urlopen):
        """When schema is provided, request includes responseMimeType + responseSchema."""
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": '{"positive_rubrics": [], "negative_rubrics": []}'}]}}]
        }).encode()
        mock_urlopen.return_value = mock_resp

        result = call_gemini("test prompt", "fake-key", schema=RUBRIC_RESPONSE_SCHEMA)

        # Verify the request body
        call_args = mock_urlopen.call_args
        req = call_args[0][0]  # Request object
        body = json.loads(req.data)
        assert body["generationConfig"]["responseMimeType"] == "application/json"
        assert "responseSchema" in body["generationConfig"]
        assert result == {"positive_rubrics": [], "negative_rubrics": []}

    @patch("urllib.request.urlopen")
    def test_structured_output_no_markdown_parsing_needed(self, mock_urlopen):
        """Structured output returns clean JSON — no fence parsing."""
        raw = '{"positive_rubrics": [{"rule": "test", "source_file": "X.md", "evidence_in_gold": "e", "category": "style"}], "negative_rubrics": []}'
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": raw}]}}]
        }).encode()
        mock_urlopen.return_value = mock_resp

        result = call_gemini("prompt", "key", schema=RUBRIC_RESPONSE_SCHEMA)
        assert len(result["positive_rubrics"]) == 1
        assert result["positive_rubrics"][0]["rule"] == "test"

    @patch("urllib.request.urlopen")
    def test_freeform_fallback_parses_markdown(self, mock_urlopen):
        """Without schema, falls back to markdown fence parsing."""
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": '```json\n{"a": 1}\n```'}]}}]
        }).encode()
        mock_urlopen.return_value = mock_resp

        result = call_gemini("prompt", "key", schema=None)
        assert result == {"a": 1}

    @patch("urllib.request.urlopen")
    def test_system_instruction_included(self, mock_urlopen):
        """systemInstruction is sent when provided."""
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": "{}"}]}}]
        }).encode()
        mock_urlopen.return_value = mock_resp

        call_gemini("prompt", "key", schema={"type": "object", "properties": {}},
                    system_instruction="You are a judge")

        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data)
        assert body["systemInstruction"]["parts"][0]["text"] == "You are a judge"

    @patch("urllib.request.urlopen")
    def test_no_candidates_returns_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({"candidates": []}).encode()
        mock_urlopen.return_value = mock_resp

        result = call_gemini("prompt", "key", schema=RUBRIC_RESPONSE_SCHEMA)
        assert "error" in result

    @patch("urllib.request.urlopen")
    def test_no_parts_returns_error_with_finish_reason(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({
            "candidates": [{"content": {"role": "model"}, "finishReason": "MAX_TOKENS"}]
        }).encode()
        mock_urlopen.return_value = mock_resp

        result = call_gemini("prompt", "key", schema=RUBRIC_RESPONSE_SCHEMA)
        assert "error" in result
        assert "MAX_TOKENS" in result["error"]

    @patch("urllib.request.urlopen")
    def test_key_in_header_not_url(self, mock_urlopen):
        """API key must be in x-goog-api-key header, not URL query param."""
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": "{}"}]}}]
        }).encode()
        mock_urlopen.return_value = mock_resp

        call_gemini("prompt", "my-secret-key", schema={"type": "object", "properties": {}})

        req = mock_urlopen.call_args[0][0]
        assert "key=" not in req.full_url
        assert req.get_header("X-goog-api-key") == "my-secret-key"


# ── construct_rubrics tests ──────────────────────────────────────────────────

class TestConstructRubrics(unittest.TestCase):

    def test_no_config_files_returns_empty(self):
        """Returns no_config_files when hierarchy has no configs."""
        task_dir = Path("/tmp/test_construct")
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "solution").mkdir(exist_ok=True)
        (task_dir / "solution" / "solve.sh").write_text("echo hi")

        with patch("taskforge.gemini_rubric_constructor.build_hierarchy_context") as mock_ctx:
            mock_ctx.return_value = {"config_hierarchy": [], "edited_paths": []}
            result = construct_rubrics(task_dir, Path("/tmp"), "fake-key")

        assert result["status"] == "no_config_files"
        assert result["positive_rubrics"] == []
        assert result["negative_rubrics"] == []

    def test_no_gemini_key(self):
        with patch("taskforge.gemini_rubric_constructor.build_hierarchy_context") as mock_ctx:
            mock_ctx.return_value = {
                "config_hierarchy": [{"path": "CLAUDE.md", "level": 0, "rule_count": 5,
                                      "directory": "(root)", "applies_to": [], "content_length": 100}],
                "edited_paths": ["src/app.ts"],
                "skills": [],
            }
            result = construct_rubrics(Path("/tmp"), Path("/tmp"), "")

        assert result["status"] == "no_gemini_key"


# ── construct_rubrics_with_kimi (legacy alias) tests ─────────────────────────
# These test the legacy alias which delegates to run_rubric_quality_loop(max_rounds=1)

class TestConstructWithKimi(unittest.TestCase):

    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_falls_back_when_no_fireworks_key(self, mock_classify):
        """Without FIREWORKS_API_KEY, returns Gemini-only result."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "HIGH",
            "quality_reasoning": "Good",
            "positive_rubrics": [{"rule": "R1", "source_file": "X.md"}],
            "negative_rubrics": [{"rule": "D1", "collision_type": "rule_conflict"}],
        }
        with patch.dict("os.environ", {"FIREWORKS_API_KEY": ""}, clear=False):
            result = construct_rubrics_with_kimi(Path("/tmp"), Path("/tmp"), "key")

        assert result["loop_metadata"]["kimi_available"] is False
        assert len(result["positive_rubrics"]) == 1

    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_kimi_confirms_all(self, mock_classify, mock_hierarchy, mock_kimi):
        """When Kimi confirms all rules, they pass through unchanged."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "HIGH",
            "quality_reasoning": "Complex",
            "positive_rubrics": [
                {"rule": "Use const", "source_file": "A.md", "evidence_in_gold": "e", "category": "style"},
            ],
            "negative_rubrics": [
                {"rule": "Run build", "source_file": "B.md", "collision_type": "scope_ambiguity",
                 "why_distracting": "waste", "severity": "medium"},
            ],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}
        mock_kimi.return_value = json.dumps({
            "task_verdict": "continue",
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "reasoning": "Confirmed in A.md", "verdict": "confirmed"},
                {"index": 0, "type": "negative", "reasoning": "Real collision", "verdict": "confirmed"},
            ],
            "additional_rules": [],
            "additional_distractors": [],
            "summary": "All good",
        })

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = construct_rubrics_with_kimi(Path("/tmp"), Path("/tmp"), "key")

        assert result["loop_metadata"]["kimi_available"] is True
        assert len(result["positive_rubrics"]) == 1
        assert len(result["negative_rubrics"]) == 1

    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_kimi_rejects_hallucinated_rule(self, mock_classify, mock_hierarchy, mock_kimi):
        """Rejected rules are dropped from output."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "HIGH",
            "quality_reasoning": "Complex",
            "positive_rubrics": [
                {"rule": "Real rule", "source_file": "A.md", "evidence_in_gold": "e", "category": "style"},
                {"rule": "Hallucinated", "source_file": "Z.md", "evidence_in_gold": "none", "category": "style"},
            ],
            "negative_rubrics": [{"rule": "D1", "collision_type": "rule_conflict"}],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}
        mock_kimi.return_value = json.dumps({
            "task_verdict": "continue",
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "reasoning": "Exists", "verdict": "confirmed"},
                {"index": 1, "type": "positive", "reasoning": "Z.md doesn't exist", "verdict": "rejected"},
                {"index": 0, "type": "negative", "reasoning": "Real", "verdict": "confirmed"},
            ],
        })

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = construct_rubrics_with_kimi(Path("/tmp"), Path("/tmp"), "key")

        assert len(result["positive_rubrics"]) == 1
        assert result["positive_rubrics"][0]["rule"] == "Real rule"

    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_kimi_revises_rule(self, mock_classify, mock_hierarchy, mock_kimi):
        """Revised rules get updated text."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "HIGH",
            "quality_reasoning": "Complex",
            "positive_rubrics": [
                {"rule": "Use let", "source_file": "A.md", "evidence_in_gold": "e", "category": "style"},
            ],
            "negative_rubrics": [{"rule": "D1", "collision_type": "rule_conflict"}],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}
        mock_kimi.return_value = json.dumps({
            "task_verdict": "continue",
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "reasoning": "Should be const not let",
                 "verdict": "revised", "revised_rule": "Use const over let"},
                {"index": 0, "type": "negative", "reasoning": "ok", "verdict": "confirmed"},
            ],
        })

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = construct_rubrics_with_kimi(Path("/tmp"), Path("/tmp"), "key")

        assert result["positive_rubrics"][0]["rule"] == "Use const over let"

    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_kimi_adds_missing_rules(self, mock_classify, mock_hierarchy, mock_kimi):
        """Kimi can add rules Gemini missed."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "HIGH",
            "quality_reasoning": "Complex",
            "positive_rubrics": [],
            "negative_rubrics": [{"rule": "D1", "collision_type": "rule_conflict"}],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}
        mock_kimi.return_value = json.dumps({
            "task_verdict": "continue",
            "rubric_verdicts": [
                {"index": 0, "type": "negative", "reasoning": "ok", "verdict": "confirmed"},
            ],
            "additional_rules": [
                {"rule": "Missing rule", "source_file": "C.md", "evidence_in_gold": "x", "category": "naming"},
            ],
            "additional_distractors": [
                {"rule": "Missing distractor", "source_file": "C.md",
                 "collision_type": "meta_confusion", "why_distracting": "y", "severity": "low"},
            ],
        })

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = construct_rubrics_with_kimi(Path("/tmp"), Path("/tmp"), "key")

        assert len(result["positive_rubrics"]) == 1
        assert result["positive_rubrics"][0]["rule"] == "Missing rule"
        assert len(result["negative_rubrics"]) >= 1


# ── Build prompt tests ───────────────────────────────────────────────────────

class TestBuildPrompt(unittest.TestCase):

    def setUp(self):
        self.task_dir = Path("/tmp/test_prompt_task")
        self.task_dir.mkdir(parents=True, exist_ok=True)
        (self.task_dir / "instruction.md").write_text("Fix the bug")
        (self.task_dir / "solution").mkdir(exist_ok=True)
        (self.task_dir / "solution" / "solve.sh").write_text("git apply patch")

    def test_prompt_includes_instruction(self):
        hierarchy = {"edited_paths": ["src/app.ts"], "config_hierarchy": [], "skills": []}
        prompt = build_rubric_prompt(self.task_dir, hierarchy, {})
        assert "Fix the bug" in prompt

    def test_prompt_includes_config_content(self):
        hierarchy = {
            "edited_paths": ["src/app.ts"],
            "config_hierarchy": [
                {"path": "CLAUDE.md", "level": 0, "rule_count": 5, "applies_to": ["src/app.ts"]},
            ],
            "skills": [],
        }
        prompt = build_rubric_prompt(self.task_dir, hierarchy, {"CLAUDE.md": "# Rules\n- Use const"})
        assert "Use const" in prompt
        assert "CLAUDE.md" in prompt

    def test_prompt_no_json_format_specification(self):
        """With structured output, prompt should NOT specify JSON format."""
        hierarchy = {"edited_paths": [], "config_hierarchy": [], "skills": []}
        prompt = build_rubric_prompt(self.task_dir, hierarchy, {})
        assert "Respond with ONLY a JSON" not in prompt


class TestBuildKimiValidationPrompt(unittest.TestCase):

    def test_includes_gemini_rubrics(self):
        gemini_result = {
            "positive_rubrics": [{"rule": "Use const", "source_file": "A.md",
                                  "source_lines": "10", "evidence_in_gold": "x", "category": "style"}],
            "negative_rubrics": [{"rule": "Run build", "source_file": "B.md",
                                  "source_lines": "5", "collision_type": "scope_ambiguity",
                                  "why_distracting": "waste", "severity": "medium"}],
            "hierarchy_analysis": "Root wins",
        }
        prompt = build_kimi_validation_prompt(gemini_result, {"A.md": "content"}, "Fix bug", "apply patch")
        assert "[P0]" in prompt
        assert "[N0]" in prompt
        assert "Use const" in prompt
        assert "Run build" in prompt
        assert "scope_ambiguity" in prompt

    def test_includes_abandon_criteria(self):
        """Kimi prompt must include research agenda abandon criteria."""
        gemini_result = {
            "positive_rubrics": [],
            "negative_rubrics": [],
            "hierarchy_analysis": "",
        }
        prompt = build_kimi_validation_prompt(gemini_result, {}, "Fix bug", "patch")
        assert "ABANDON" in prompt
        assert "task_verdict" in prompt
        assert "Zero distractors" in prompt
        assert "instruction discrimination" in prompt

    def test_includes_quality_context(self):
        """Kimi prompt includes Gemini's quality assessment when available."""
        gemini_result = {
            "positive_rubrics": [],
            "negative_rubrics": [],
            "hierarchy_analysis": "",
            "quality_verdict": "HIGH",
            "quality_reasoning": "Complex hierarchy",
            "meta_referential": True,
            "competing_principles": True,
            "config_navigation": "deep_hierarchy",
        }
        prompt = build_kimi_validation_prompt(gemini_result, {}, "Fix bug", "patch")
        assert "HIGH" in prompt
        assert "Complex hierarchy" in prompt
        assert "meta_referential" in prompt.lower() or "Meta-referential" in prompt

    def test_round_context_included(self):
        """Round 2+ prompts include previous feedback summary."""
        gemini_result = {
            "positive_rubrics": [{"rule": "R1", "source_file": "A.md"}],
            "negative_rubrics": [],
            "hierarchy_analysis": "",
        }
        prompt = build_kimi_validation_prompt(
            gemini_result, {}, "Fix bug", "patch",
            round_num=2, previous_feedback="Rules P0 and P1 were weak",
        )
        assert "round 2" in prompt.lower()
        assert "Previous Round Feedback" in prompt
        assert "Rules P0 and P1 were weak" in prompt


# ── _apply_kimi_verdicts tests ─────────────────────────────────────────────

class TestApplyKimiVerdicts(unittest.TestCase):

    def test_confirmed_rules_pass_through(self):
        gemini = {
            "positive_rubrics": [{"rule": "R1"}, {"rule": "R2"}],
            "negative_rubrics": [{"rule": "D1"}],
        }
        kimi = {
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "verdict": "confirmed", "reasoning": "ok"},
                {"index": 1, "type": "positive", "verdict": "confirmed", "reasoning": "ok"},
                {"index": 0, "type": "negative", "verdict": "confirmed", "reasoning": "ok"},
            ],
        }
        pos, neg = _apply_kimi_verdicts(gemini, kimi)
        assert len(pos) == 2
        assert len(neg) == 1

    def test_rejected_rules_dropped(self):
        gemini = {
            "positive_rubrics": [{"rule": "Good"}, {"rule": "Bad"}],
            "negative_rubrics": [],
        }
        kimi = {
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "verdict": "confirmed", "reasoning": "ok"},
                {"index": 1, "type": "positive", "verdict": "rejected", "reasoning": "hallucinated"},
            ],
        }
        pos, neg = _apply_kimi_verdicts(gemini, kimi)
        assert len(pos) == 1
        assert pos[0]["rule"] == "Good"

    def test_revised_rules_updated(self):
        gemini = {
            "positive_rubrics": [{"rule": "Use let"}],
            "negative_rubrics": [],
        }
        kimi = {
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "verdict": "revised",
                 "reasoning": "should be const", "revised_rule": "Use const"},
            ],
        }
        pos, neg = _apply_kimi_verdicts(gemini, kimi)
        assert pos[0]["rule"] == "Use const"

    def test_additional_rules_appended(self):
        gemini = {"positive_rubrics": [], "negative_rubrics": []}
        kimi = {
            "rubric_verdicts": [],
            "additional_rules": [{"rule": "Extra positive"}],
            "additional_distractors": [{"rule": "Extra distractor"}],
        }
        pos, neg = _apply_kimi_verdicts(gemini, kimi)
        assert len(pos) == 1
        assert len(neg) == 1

    def test_out_of_range_index_ignored(self):
        gemini = {"positive_rubrics": [{"rule": "Only one"}], "negative_rubrics": []}
        kimi = {
            "rubric_verdicts": [
                {"index": 5, "type": "positive", "verdict": "confirmed", "reasoning": "?"},
            ],
        }
        pos, neg = _apply_kimi_verdicts(gemini, kimi)
        assert len(pos) == 0  # index 5 doesn't exist


# ── _build_gemini_reevaluation_prompt tests ─────────────────────────────────

class TestBuildGeminiReevalPrompt(unittest.TestCase):

    def test_includes_kimi_feedback(self):
        base = "Original prompt content"
        kimi_feedback = {
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "verdict": "rejected",
                 "reasoning": "File doesn't exist"},
                {"index": 0, "type": "negative", "verdict": "revised",
                 "reasoning": "Wrong collision type", "revised_rule": "Better rule"},
            ],
            "summary": "Half the rules were wrong",
        }
        prompt = _build_gemini_reevaluation_prompt(base, kimi_feedback, round_num=1)
        assert "Original prompt content" in prompt
        assert "Kimi Validation Feedback" in prompt
        assert "rejected" in prompt
        assert "File doesn't exist" in prompt
        assert "Better rule" in prompt
        assert "Half the rules were wrong" in prompt

    def test_includes_additional_rules_from_kimi(self):
        kimi_feedback = {
            "rubric_verdicts": [],
            "additional_rules": [{"rule": "Missed rule", "source_file": "X.md"}],
            "additional_distractors": [{"rule": "Missed dist", "collision_type": "meta_confusion"}],
        }
        prompt = _build_gemini_reevaluation_prompt("base", kimi_feedback, round_num=2)
        assert "Missed rule" in prompt
        assert "Missed dist" in prompt
        assert "meta_confusion" in prompt


# ── run_rubric_quality_loop tests ──────────────────────────────────────────

class TestRunRubricQualityLoop(unittest.TestCase):

    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_delete_verdict_abandons_immediately(self, mock_classify):
        """DELETE quality verdict → abandoned, no Kimi call."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "DELETE",
            "quality_reasoning": "No config files",
            "positive_rubrics": [],
            "negative_rubrics": [],
        }
        result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key")
        assert result["status"] == "abandoned"
        assert result["loop_metadata"]["abandoned_by"] == "gemini"
        assert result["loop_metadata"]["rounds"] == 0

    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_low_zero_distractors_abandons(self, mock_classify):
        """LOW + 0 distractors → abandoned before Kimi."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "LOW",
            "quality_reasoning": "Mechanical edit",
            "positive_rubrics": [{"rule": "R1"}],
            "negative_rubrics": [],
        }
        result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key")
        assert result["status"] == "abandoned"
        assert "zero distractors" in result["loop_metadata"]["abandon_reason"].lower()

    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_low_with_distractors_continues(self, mock_classify):
        """LOW + distractors present → not auto-abandoned (Kimi decides)."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "LOW",
            "quality_reasoning": "Simple",
            "positive_rubrics": [{"rule": "R1"}],
            "negative_rubrics": [{"rule": "D1", "collision_type": "rule_conflict"}],
        }
        with patch.dict("os.environ", {"FIREWORKS_API_KEY": ""}, clear=False):
            result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key")
        # No Kimi available, but not auto-abandoned
        assert result["status"] == "ok"
        assert result["loop_metadata"]["kimi_available"] is False

    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_kimi_abandon_kills_task(self, mock_classify, mock_hierarchy, mock_kimi):
        """Kimi returning task_verdict='abandon' kills the task."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "MEDIUM",
            "quality_reasoning": "Some signal",
            "positive_rubrics": [{"rule": "R1", "source_file": "A.md"}],
            "negative_rubrics": [],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}
        mock_kimi.return_value = json.dumps({
            "task_verdict": "abandon",
            "abandon_reason": "All rules are trivially simple README formatting",
            "rubric_verdicts": [],
            "summary": "Not worth keeping",
        })

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key")

        assert result["status"] == "abandoned"
        assert result["loop_metadata"]["abandoned_by"] == "kimi"
        assert "README formatting" in result["loop_metadata"]["abandon_reason"]

    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_kimi_confirms_all_single_round(self, mock_classify, mock_hierarchy, mock_kimi):
        """All confirmed → done in 1 round, no re-evaluation."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "HIGH",
            "quality_reasoning": "Complex",
            "positive_rubrics": [{"rule": "Use const", "source_file": "A.md"}],
            "negative_rubrics": [{"rule": "Run all", "source_file": "B.md",
                                  "collision_type": "scope_ambiguity"}],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}
        mock_kimi.return_value = json.dumps({
            "task_verdict": "continue",
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "verdict": "confirmed", "reasoning": "ok"},
                {"index": 0, "type": "negative", "verdict": "confirmed", "reasoning": "ok"},
            ],
        })

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key")

        assert result["status"] == "ok"
        assert result["loop_metadata"]["rounds"] == 1
        assert len(result["positive_rubrics"]) == 1
        assert len(result["negative_rubrics"]) == 1

    @patch("taskforge.gemini_rubric_constructor.call_gemini")
    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_rejection_triggers_gemini_reeval(self, mock_classify, mock_hierarchy,
                                              mock_kimi, mock_gemini):
        """Kimi rejection in round 1 triggers Gemini re-evaluation in round 2."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "HIGH",
            "quality_reasoning": "Complex",
            "positive_rubrics": [
                {"rule": "Good rule", "source_file": "A.md"},
                {"rule": "Bad rule", "source_file": "Z.md"},
            ],
            "negative_rubrics": [],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}

        # Round 1: Kimi rejects one rule
        # Round 2: Kimi confirms all
        mock_kimi.side_effect = [
            json.dumps({
                "task_verdict": "continue",
                "rubric_verdicts": [
                    {"index": 0, "type": "positive", "verdict": "confirmed", "reasoning": "ok"},
                    {"index": 1, "type": "positive", "verdict": "rejected", "reasoning": "Z.md doesn't exist"},
                ],
                "summary": "One hallucinated",
            }),
            json.dumps({
                "task_verdict": "continue",
                "rubric_verdicts": [
                    {"index": 0, "type": "positive", "verdict": "confirmed", "reasoning": "ok"},
                ],
            }),
        ]

        # Gemini re-eval returns updated rubrics (dropped bad rule)
        mock_gemini.return_value = {
            "positive_rubrics": [{"rule": "Good rule", "source_file": "A.md"}],
            "negative_rubrics": [{"rule": "New distractor", "source_file": "B.md",
                                  "collision_type": "rule_conflict"}],
            "quality_verdict": "HIGH",
            "quality_reasoning": "Still complex",
        }

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key", max_rounds=3)

        assert result["status"] == "ok"
        assert result["loop_metadata"]["rounds"] == 2
        # Gemini re-eval was called once
        mock_gemini.assert_called_once()

    @patch("taskforge.gemini_rubric_constructor.call_gemini")
    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_max_rounds_kimi_final_word(self, mock_classify, mock_hierarchy,
                                        mock_kimi, mock_gemini):
        """After max rounds, Kimi's last verdicts are applied (final word)."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "MEDIUM",
            "quality_reasoning": "OK",
            "positive_rubrics": [{"rule": "R1"}, {"rule": "R2"}, {"rule": "R3"}],
            "negative_rubrics": [],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}

        # All 3 rounds: Kimi keeps rejecting R3
        kimi_response = json.dumps({
            "task_verdict": "continue",
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "verdict": "confirmed", "reasoning": "ok"},
                {"index": 1, "type": "positive", "verdict": "confirmed", "reasoning": "ok"},
                {"index": 2, "type": "positive", "verdict": "rejected", "reasoning": "hallucinated"},
            ],
        })
        mock_kimi.side_effect = [kimi_response, kimi_response, kimi_response]

        # Gemini re-evals still include R3
        mock_gemini.return_value = {
            "positive_rubrics": [{"rule": "R1"}, {"rule": "R2"}, {"rule": "R3"}],
            "negative_rubrics": [],
            "quality_verdict": "MEDIUM",
        }

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key", max_rounds=3)

        assert result["status"] == "ok"
        assert result["loop_metadata"]["rounds"] == 3
        # Kimi's final word: R3 rejected
        rules = [r["rule"] for r in result["positive_rubrics"]]
        assert "R1" in rules
        assert "R2" in rules
        assert "R3" not in rules

    @patch("taskforge.gemini_rubric_constructor.call_kimi")
    @patch("taskforge.gemini_rubric_constructor.build_hierarchy_context")
    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_all_rejected_after_max_rounds_abandons(self, mock_classify, mock_hierarchy, mock_kimi):
        """If Kimi rejects ALL rules after max rounds → abandoned."""
        mock_classify.return_value = {
            "status": "ok",
            "quality_verdict": "MEDIUM",
            "quality_reasoning": "OK",
            "positive_rubrics": [{"rule": "Bad1"}],
            "negative_rubrics": [{"rule": "Bad2"}],
        }
        mock_hierarchy.return_value = {"config_hierarchy": [], "edited_paths": []}
        mock_kimi.return_value = json.dumps({
            "task_verdict": "continue",
            "rubric_verdicts": [
                {"index": 0, "type": "positive", "verdict": "rejected", "reasoning": "wrong"},
                {"index": 0, "type": "negative", "verdict": "rejected", "reasoning": "wrong"},
            ],
        })

        with patch.dict("os.environ", {"FIREWORKS_API_KEY": "fake"}, clear=False):
            result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key", max_rounds=1)

        assert result["status"] == "abandoned"
        assert "All rubrics rejected" in result["loop_metadata"]["abandon_reason"]

    @patch("taskforge.gemini_rubric_constructor.construct_and_classify")
    def test_gemini_error_propagated(self, mock_classify):
        """Gemini error in initial call is propagated."""
        mock_classify.return_value = {"status": "gemini_error", "error": "timeout"}
        result = run_rubric_quality_loop(Path("/tmp"), Path("/tmp"), "key")
        assert result["status"] == "gemini_error"


if __name__ == "__main__":
    unittest.main()
