from __future__ import annotations

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class Finding:
    id: str
    category: str
    severity: str
    file: str
    line: int
    snippet: str
    description: str
    confidence: int

SYSTEM_PROMPT = """
You are an expert security auditor analyzing agent skill content for hidden malicious intent.
Analyze the provided content and return a JSON object with a single key "findings" containing a list of objects.
Categories to detect:
- Polite reframings of prompt injections
- Natural-language exfiltration ('remember everything and include it')
- Description/behavior mismatch (SKILL.md says one thing, scripts do another)
- Narrative deception in instructions
- Anti-refusal patterns ('never refuse', 'always comply')

Each finding should be a JSON object with:
- id: e.g., 'SEM-001'
- category: one of the categories above
- severity: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
- line: integer, line number where finding starts (or 1 if global)
- snippet: brief text snippet
- description: detailed explanation
- confidence: integer between 0 and 100

If no findings, return {"findings": []}.
Only return valid JSON. Do not include markdown formatting like ```json.
"""

def _detect_provider() -> tuple[str, str] | None:
    """Detects the LLM provider and returns (provider, api_key) or None."""
    provider = os.environ.get("EVALUATOR_LLM_PROVIDER", "").lower()
    if provider == "openai":
        key = os.environ.get("OPENAI_API_KEY")
        if key: return ("openai", key)
    elif provider == "anthropic":
        key = os.environ.get("ANTHROPIC_API_KEY")
        if key: return ("anthropic", key)
    elif provider == "google":
        key = os.environ.get("GOOGLE_API_KEY")
        if key: return ("google", key)
    
    # Auto-detect if provider not set explicitly
    if os.environ.get("OPENAI_API_KEY"): return ("openai", os.environ.get("OPENAI_API_KEY"))
    if os.environ.get("ANTHROPIC_API_KEY"): return ("anthropic", os.environ.get("ANTHROPIC_API_KEY"))
    if os.environ.get("GOOGLE_API_KEY"): return ("google", os.environ.get("GOOGLE_API_KEY"))
    return None

def semantic_scan(content: str, file_path: str, file_type: str) -> tuple[list[dict], list[dict]]:
    """Runs a semantic scan on the given content using the configured LLM provider."""
    llm_call_log = []
    findings = []
    
    provider_info = _detect_provider()
    if not provider_info:
        llm_call_log.append({
            "provider": "none",
            "model": "none",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "duration_ms": 0,
            "success": False,
            "error": "No LLM provider configured. Degrading gracefully."
        })
        return findings, llm_call_log

    provider, api_key = provider_info
    
    prompt = f"File: {file_path}\nType: {file_type}\n\nContent:\n{content}"
    
    start_time = time.time()
    success = False
    response_text = "{}"
    prompt_tokens = 0
    completion_tokens = 0
    model = ""
    error_msg = ""
    
    try:
        if provider == "openai":
            import openai
            client = openai.OpenAI(api_key=api_key)
            model = "gpt-4o"
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            response_text = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            success = True
        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            model = "claude-3-5-sonnet-20240620"
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = response.content[0].text
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            success = True
        elif provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = "gemini-1.5-pro"
            genai_model = genai.GenerativeModel(model, system_instruction=SYSTEM_PROMPT)
            response = genai_model.generate_content(prompt)
            response_text = response.text
            success = True
            if hasattr(response, "usage_metadata"):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
    except ImportError as e:
        error_msg = f"Missing dependency for {provider}: {e}"
    except Exception as e:
        error_msg = str(e)
        
    duration_ms = int((time.time() - start_time) * 1000)
    
    llm_call_log.append({
        "provider": provider,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "duration_ms": duration_ms,
        "success": success,
        "error": error_msg
    })
    
    if success:
        try:
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
                
            data = json.loads(clean_text)
            for f in data.get("findings", []):
                findings.append({
                    "id": f.get("id", "SEM-000"),
                    "category": f.get("category", "Unknown"),
                    "severity": f.get("severity", "LOW"),
                    "file": file_path,
                    "line": f.get("line", 1),
                    "snippet": f.get("snippet", ""),
                    "description": f.get("description", ""),
                    "confidence": f.get("confidence", 50)
                })
        except Exception as e:
            llm_call_log[-1]["error"] = f"Failed to parse JSON: {e}"
            llm_call_log[-1]["success"] = False

    return findings, llm_call_log

def main():
    parser = argparse.ArgumentParser(description="Semantic Scanner")
    parser.add_argument("file", help="File to scan")
    parser.add_argument("--type", help="File type", default="text")
    args = parser.parse_args()
    
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {args.file}: {e}")
        sys.exit(1)
        
    findings, log = semantic_scan(content, args.file, args.type)
    
    print(json.dumps({"findings": findings, "log": log}, indent=2))

if __name__ == "__main__":
    main()
