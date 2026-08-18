"""Proposes improved skill descriptions based on trigger test failures.
Uses 'pushy' strategy: aggressively lists edge-case triggering scenarios."""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

def improve_description(current_description: str, failures: dict) -> str:
    """Given current description and FP/FN failures, generates improved description.
    Uses LLM if available, otherwise applies heuristic rules."""
    
    # Provider integration would go here
    provider = os.environ.get('EVALUATOR_LLM_PROVIDER')
    
    # 1. Keep under 1024 chars
    # 2. Add edge-case scenarios for false negatives
    # 3. Add exclusion clauses for false positives
    # 4. Use 'pushy' language: 'Use when...', 'Trigger on...'
    
    new_desc = current_description
    if not new_desc.startswith("Use when") and not new_desc.startswith("Trigger on"):
        new_desc = f"Trigger on {new_desc.lower()}"
        
    fn_queries = failures.get('false_negatives', [])
    fp_queries = failures.get('false_positives', [])
    
    if fn_queries:
        new_desc += ". Also triggers for: " + ", ".join([q[:20] for q in fn_queries[:3]])
        
    if fp_queries:
        new_desc += ". DO NOT trigger for: " + ", ".join([q[:20] for q in fp_queries[:3]])
        
    # truncate
    if len(new_desc) > 1024:
        new_desc = new_desc[:1020] + "..."
        
    return new_desc

def main():
    parser = argparse.ArgumentParser(description='Improve skill description based on failures')
    parser.add_argument('--desc', required=True, help='Current description')
    parser.add_argument('--failures', required=True, help='Path to failures JSON')
    args = parser.parse_args()
    
    if Path(args.failures).exists():
        with open(args.failures, 'r') as f:
            failures = json.load(f)
    else:
        failures = {}
        
    improved = improve_description(args.desc, failures)
    print(improved)

if __name__ == "__main__":
    main()
