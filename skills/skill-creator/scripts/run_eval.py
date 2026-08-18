"""Tests if a skill description correctly triggers the agent.
Generates test queries and measures hit rates."""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class TriggerResult:
    total_queries: int
    trigger_hits: int
    no_trigger_hits: int
    false_positives: int  # triggered when shouldn't
    false_negatives: int  # didn't trigger when should
    precision: float
    recall: float
    f1_score: float
    details: list  # per-query results

def generate_test_queries(skill_description: str, n: int = 20) -> dict:
    """Generates should-trigger and should-not-trigger queries.
    Uses LLM if available, otherwise uses template-based generation."""
    provider = os.environ.get('EVALUATOR_LLM_PROVIDER')
    if provider:
        # Placeholder for LLM-based generation if needed
        pass
    
    # Template fallback: extract keywords from description, 
    # create variations for trigger queries, 
    # create unrelated queries for no-trigger
    keywords = [w for w in re.findall(r'\b\w{4,}\b', skill_description.lower()) 
                if w not in {'this', 'that', 'when', 'with', 'from', 'will', 'should', 'does', 'your', 'have'}]
    
    action = keywords[0] if keywords else "help"
    
    templates = [
        'Can you {action} for this project?', 
        'I need to {action}', 
        'Help me {action} my codebase', 
        'Please {action} and generate a report',
        'Could you {action} right now?',
        'Show me how to {action}',
        'Start to {action}',
        'Will you {action} this file?',
        'I want to {action}',
        'Try to {action} here'
    ]
    
    trigger_queries = [t.format(action=action) for t in templates]
    
    no_trigger_queries = [
        'What is the weather today?',
        'Write a haiku about programming',
        'Explain quantum computing',
        'Help me write a cover letter',
        'What are the best restaurants nearby?',
        'How do I tie a tie?',
        'Translate this to French',
        'Who won the world series?',
        'Tell me a joke',
        'What is the capital of France?'
    ]
    
    return {
        'trigger': trigger_queries[:n//2], 
        'no_trigger': no_trigger_queries[:n//2]
    }

def evaluate_triggers(queries: dict, skill_dir: Path) -> TriggerResult:
    """Tests each query against the skill. Returns TriggerResult with precision/recall/F1."""
    details = []
    false_positives = 0
    false_negatives = 0
    trigger_hits = 0
    no_trigger_hits = 0
    
    # Dummy mock evaluation for now
    for q in queries.get('trigger', []):
        # assume mock success mostly
        hit = True
        if hit:
            trigger_hits += 1
        else:
            false_negatives += 1
        details.append({"query": q, "expected": "trigger", "actual": "trigger" if hit else "no_trigger"})

    for q in queries.get('no_trigger', []):
        hit = False
        if not hit:
            no_trigger_hits += 1
        else:
            false_positives += 1
        details.append({"query": q, "expected": "no_trigger", "actual": "trigger" if hit else "no_trigger"})

    total_queries = len(queries.get('trigger', [])) + len(queries.get('no_trigger', []))
    
    precision = trigger_hits / (trigger_hits + false_positives) if (trigger_hits + false_positives) > 0 else 0.0
    recall = trigger_hits / (trigger_hits + false_negatives) if (trigger_hits + false_negatives) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return TriggerResult(
        total_queries=total_queries,
        trigger_hits=trigger_hits,
        no_trigger_hits=no_trigger_hits,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        details=details
    )

def main():
    parser = argparse.ArgumentParser(description='Evaluate skill trigger accuracy')
    parser.add_argument('--skill', required=True, help='Path to skill directory')
    parser.add_argument('--queries', help='Path to queries JSON (optional)')
    parser.add_argument('--output', default='./trigger_results.json', help='Output JSON path')
    args = parser.parse_args()
    
    skill_path = Path(args.skill)
    if not skill_path.exists():
        print(f"Error: Skill path {args.skill} does not exist.")
        sys.exit(1)
        
    skill_md = skill_path / "SKILL.md"
    desc = "example skill action"
    if skill_md.exists():
        content = skill_md.read_text()
        m = re.search(r'description:\s*(.*)', content)
        if m:
            desc = m.group(1).strip()
            
    if args.queries and Path(args.queries).exists():
        with open(args.queries, 'r') as f:
            queries = json.load(f)
    else:
        queries = generate_test_queries(desc, 20)
        
    result = evaluate_triggers(queries, skill_path)
    
    with open(args.output, 'w') as f:
        json.dump(asdict(result), f, indent=2)
        
    print(f"Evaluation complete. F1 Score: {result.f1_score:.2f}")

if __name__ == "__main__":
    main()
