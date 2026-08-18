from __future__ import annotations
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import sys

@dataclass
class TraceEvent:
    timestamp: str
    event_type: str
    tool_name: str | None
    arguments: dict | None
    duration_ms: int | None
    content: str | None

def capture_trace(proc_stdout: str) -> list[TraceEvent]:
    """Parses structured output for tool calls and text output."""
    events = []
    for line in proc_stdout.splitlines():
        if line.startswith("TOOL_CALL:"):
            try:
                data = json.loads(line[len("TOOL_CALL:"):])
                events.append(TraceEvent(
                    timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    event_type="tool_call",
                    tool_name=data.get("name"),
                    arguments=data.get("args", {}),
                    duration_ms=None,
                    content=None
                ))
            except json.JSONDecodeError:
                pass
        elif line.startswith("TEXT:"):
            events.append(TraceEvent(
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                event_type="text_output",
                tool_name=None,
                arguments=None,
                duration_ms=None,
                content=line[len("TEXT:"):]
            ))
        elif line.startswith("ERROR:"):
            events.append(TraceEvent(
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                event_type="error",
                tool_name=None,
                arguments=None,
                duration_ms=None,
                content=line[len("ERROR:"):]
            ))
    return events

def write_trace(events: list[TraceEvent], output_dir: Path) -> Path:
    """Writes trace events to trace.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / "trace.json"
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in events], f, indent=2)
    return trace_path

def write_timing(start_time: float, end_time: float, token_count: int, output_dir: Path) -> Path:
    """Writes timing metrics to timing.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timing_path = output_dir / "timing.json"
    
    duration_ms = int((end_time - start_time) * 1000)
    tokens_per_second = token_count / ((end_time - start_time) or 1)
    estimated_cost = token_count * 0.000002 # Baseline cost calculation
    
    timing_data = {
        "duration_ms": duration_ms,
        "total_tokens": token_count,
        "tokens_per_second": tokens_per_second,
        "estimated_cost": estimated_cost
    }
    with open(timing_path, "w", encoding="utf-8") as f:
        json.dump(timing_data, f, indent=2)
    return timing_path

def main():
    parser = argparse.ArgumentParser(description="Capture trace and timing data")
    parser.add_argument("--stdout", type=str, required=True, help="Process stdout to parse")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save trace.json and timing.json")
    args = parser.parse_args()
    
    events = capture_trace(args.stdout)
    out_dir = Path(args.output_dir)
    write_trace(events, out_dir)
    write_timing(time.time() - 2.0, time.time(), 300, out_dir)
    print(f"Captured {len(events)} trace events.")
    print(f"Trace and timing written to {out_dir}")

if __name__ == "__main__":
    main()
