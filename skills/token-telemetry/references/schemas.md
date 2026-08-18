# 📋 TokenTelemetry Schema Specifications

This document defines the schema contracts for individual session telemetry events and aggregate multi-project reports.

---

## 📊 Session Telemetry Record Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SessionTelemetry",
  "type": "object",
  "required": [
    "session_id",
    "agent",
    "model",
    "total_tokens",
    "cost_usd",
    "cost_inr",
    "cache_hit_ratio"
  ],
  "properties": {
    "session_id": { "type": "string" },
    "agent": { "type": "string", "enum": ["Claude Code", "Antigravity (Gemini CLI)", "Cursor", "Hermes Agent", "OpenAI Codex", "AI Agent"] },
    "model": { "type": "string" },
    "project_path": { "type": "string" },
    "start_time": { "type": "string" },
    "duration_seconds": { "type": "number", "minimum": 0 },
    "input_tokens": { "type": "integer", "minimum": 0 },
    "output_tokens": { "type": "integer", "minimum": 0 },
    "cache_read_tokens": { "type": "integer", "minimum": 0 },
    "cache_write_tokens": { "type": "integer", "minimum": 0 },
    "reasoning_tokens": { "type": "integer", "minimum": 0 },
    "total_tokens": { "type": "integer", "minimum": 0 },
    "cost_usd": { "type": "number", "minimum": 0 },
    "cost_inr": { "type": "number", "minimum": 0 },
    "tokens_per_second": { "type": "number", "minimum": 0 },
    "cache_hit_ratio": { "type": "number", "minimum": 0, "maximum": 100 },
    "tool_calls": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "count": { "type": "integer", "minimum": 1 }
        }
      }
    }
  }
}
```
