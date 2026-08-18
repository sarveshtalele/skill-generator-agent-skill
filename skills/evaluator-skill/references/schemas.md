# Evaluation Output Schemas

Reference document defining JSON schemas for all evaluation output artifacts. Load this file when you need to generate or interpret evaluation outputs.

## `evals.json` — Test Case Definitions

```json
{
  "skill_name": "string — kebab-case skill name",
  "evals": [
    {
      "id": "string — unique test ID (e.g. eval-001)",
      "prompt": "string — natural language user prompt to test",
      "expected_output": "string — plain text description of expected behavior",
      "files": ["string[] — fixture file paths to inject into workspace before test"],
      "assertions": [
        "contains:<text>    — case-insensitive substring match",
        "matches:<regex>    — regex pattern match",
        "file:<path>        — verify file exists in workspace",
        "json:<key.path>    — parse JSON output, verify key exists",
        "<semantic text>    — LLM semantic grading (no prefix)"
      ]
    }
  ]
}
```

## `grading.json` — Assertion Results

```json
{
  "skill_name": "string",
  "eval_id": "string",
  "timestamp": "string — ISO 8601",
  "results": [
    {
      "assertion": "string — the original assertion text",
      "assertion_type": "contains | matches | file | json | semantic",
      "passed": "boolean",
      "evidence": "string — quoted evidence from output supporting pass/fail",
      "reason": "string — explanation of why it passed or failed"
    }
  ],
  "pass_rate": "float — 0.0 to 1.0",
  "total": "int",
  "passed": "int",
  "failed": "int"
}
```

## `trace.json` — Execution Trace

```json
{
  "skill_name": "string",
  "eval_id": "string",
  "events": [
    {
      "timestamp": "string — ISO 8601",
      "event_type": "tool_call | tool_result | text_output | error",
      "tool_name": "string | null",
      "arguments": "object | null",
      "duration_ms": "int | null",
      "content": "string | null"
    }
  ],
  "total_events": "int",
  "total_tool_calls": "int"
}
```

## `timing.json` — Performance Telemetry

```json
{
  "skill_name": "string",
  "eval_id": "string",
  "duration_ms": "int — total wall-clock time",
  "total_tokens": "int — input + output tokens consumed",
  "tokens_per_second": "float",
  "estimated_cost_usd": "float | null"
}
```

## `benchmark.json` — Baseline Comparison

```json
{
  "skill_name": "string",
  "timestamp": "string — ISO 8601",
  "with_skill": {
    "pass_rate": "float",
    "avg_duration_ms": "int",
    "avg_tokens": "int"
  },
  "without_skill": {
    "pass_rate": "float",
    "avg_duration_ms": "int",
    "avg_tokens": "int"
  },
  "lift": {
    "pass_rate_delta": "float — with - without",
    "time_delta_ms": "int",
    "token_delta": "int",
    "lift_score": "float — 0-100 composite"
  }
}
```

## `comparison.json` — Blind A/B Comparison

```json
{
  "eval_id": "string",
  "output_a_label": "string — revealed after grading",
  "output_b_label": "string — revealed after grading",
  "rubric": {
    "content_quality": { "a_score": "int 1-10", "b_score": "int 1-10" },
    "structure": { "a_score": "int 1-10", "b_score": "int 1-10" },
    "completeness": { "a_score": "int 1-10", "b_score": "int 1-10" }
  },
  "winner": "A | B | TIE",
  "reasoning": "string"
}
```

## `analysis.json` — Post-Hoc Analysis

```json
{
  "eval_id": "string",
  "winner_skill": "string",
  "loser_skill": "string",
  "improvements": [
    {
      "area": "string — e.g. 'Error handling'",
      "suggestion": "string — actionable improvement",
      "priority": "high | medium | low"
    }
  ],
  "trends": ["string — broad patterns observed"]
}
```

## `feedback.json` — Human Review Feedback

```json
{
  "eval_id": "string",
  "reviewer": "string",
  "timestamp": "string — ISO 8601",
  "overall_rating": "int 1-5",
  "comments": "string",
  "per_assertion_overrides": [
    {
      "assertion": "string",
      "original_grade": "pass | fail",
      "override_grade": "pass | fail",
      "reason": "string"
    }
  ]
}
```
