# 📋 Token Telemetry JSON Schemas

This document defines the schema contracts for telemetry events and output summaries.

---

## 📊 Token Record Schema (`telemetry.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TokenRecord",
  "type": "object",
  "required": [
    "session_id",
    "model",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "estimated_cost_usd",
    "cache_hit_ratio"
  ],
  "properties": {
    "session_id": { "type": "string" },
    "model": { "type": "string" },
    "input_tokens": { "type": "integer", "minimum": 0 },
    "output_tokens": { "type": "integer", "minimum": 0 },
    "cache_read_tokens": { "type": "integer", "minimum": 0 },
    "cache_write_tokens": { "type": "integer", "minimum": 0 },
    "duration_seconds": { "type": "number", "minimum": 0 },
    "total_tokens": { "type": "integer", "minimum": 0 },
    "estimated_cost_usd": { "type": "number", "minimum": 0 },
    "tokens_per_second": { "type": "number", "minimum": 0 },
    "cache_hit_ratio": { "type": "number", "minimum": 0, "maximum": 100 }
  }
}
```
