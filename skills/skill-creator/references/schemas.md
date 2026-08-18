# Skill Creator Interop Formats (JSON Schemas)

## evals.json
Defines the test cases for evaluating a skill.
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "prompt": { "type": "string" },
      "expected_behavior": { "type": "string" },
      "files": {
        "type": "object",
        "additionalProperties": { "type": "string" }
      }
    },
    "required": ["id", "prompt"]
  }
}
```

## grading.json
Assertion results from the grader agent.
```json
{
  "type": "object",
  "additionalProperties": {
    "type": "object",
    "properties": {
      "passed": { "type": "boolean" },
      "reasoning": { "type": "string" },
      "metrics": {
        "type": "object",
        "properties": {
          "time_s": { "type": "number" },
          "tokens": { "type": "integer" }
        }
      }
    },
    "required": ["passed"]
  }
}
```

## comparison.json
Blind A/B comparison results.
```json
{
  "type": "object",
  "properties": {
    "winner": { "enum": ["A", "B", "tie"] },
    "rationale": { "type": "string" }
  }
}
```

## analysis.json
Post-hoc analysis.
```json
{
  "type": "object",
  "properties": {
    "summary": { "type": "string" },
    "failure_modes": {
      "type": "array",
      "items": { "type": "string" }
    },
    "recommendations": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

## feedback.json
Human review feedback.
```json
{
  "type": "object",
  "additionalProperties": {
    "type": "string",
    "description": "Feedback text indexed by case ID"
  }
}
```

## optimization_report.json
Trigger optimization results.
```json
{
  "type": "object",
  "properties": {
    "trigger_prompt": { "type": "string" },
    "precision": { "type": "number" },
    "recall": { "type": "number" },
    "false_positives": { "type": "array", "items": { "type": "string" } },
    "false_negatives": { "type": "array", "items": { "type": "string" } }
  }
}
```
