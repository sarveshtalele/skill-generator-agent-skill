from __future__ import annotations
import re
import argparse
import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class YaraRule:
    name: str
    meta: dict[str, str]
    strings: dict[str, tuple[str, bool]] # name -> (pattern, nocase)
    condition: str

def load_rules(rules_path: Path) -> list[YaraRule]:
    content = rules_path.read_text()
    rules = []
    
    rule_blocks = re.findall(r'rule\s+(\w+)\s*\{([^}]*)\}', content, re.DOTALL)
    for name, body in rule_blocks:
        meta_match = re.search(r'meta:\s*(.*?)(?=strings:|condition:|$)', body, re.DOTALL)
        meta = {}
        if meta_match:
            for line in meta_match.group(1).strip().splitlines():
                if '=' in line:
                    k, v = line.split('=', 1)
                    meta[k.strip()] = v.strip().strip('"')
                    
        strings_match = re.search(r'strings:\s*(.*?)(?=condition:|$)', body, re.DOTALL)
        strings = {}
        if strings_match:
            for line in strings_match.group(1).strip().splitlines():
                line = line.strip()
                if line.startswith('$'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        var_name = parts[0].strip()
                        val_part = parts[1].strip()
                        nocase = 'nocase' in val_part.lower()
                        val = re.search(r'"([^"]*)"', val_part)
                        if val:
                            strings[var_name] = (val.group(1), nocase)
                            
        condition_match = re.search(r'condition:\s*(.*)', body, re.DOTALL)
        condition = condition_match.group(1).strip() if condition_match else ""
        
        rules.append(YaraRule(name, meta, strings, condition))
        
    return rules

def evaluate_condition(condition: str, matched_vars: set[str]) -> bool:
    import ast
    cond = condition
    for var in sorted(matched_vars, key=len, reverse=True):
        cond = cond.replace(var, "True")
    
    cond = re.sub(r'\$[a-zA-Z0-9_]+', "False", cond)
    
    try:
        tree = ast.parse(cond, mode='eval')
        def eval_node(node):
            if isinstance(node, ast.Expression):
                return eval_node(node.body)
            elif isinstance(node, ast.Constant):
                return bool(node.value)
            elif isinstance(node, ast.Name):
                return node.id == "True"
            elif isinstance(node, ast.BoolOp):
                if isinstance(node.op, ast.And):
                    return all(eval_node(v) for v in node.values)
                elif isinstance(node.op, ast.Or):
                    return any(eval_node(v) for v in node.values)
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                return not eval_node(node.operand)
            return False
        return eval_node(tree)
    except Exception:
        return False

def scan_content(content: str, rules: list[YaraRule], filepath: str) -> list[dict]:
    findings = []
    lines = content.splitlines()
    
    for rule in rules:
        matched_vars = set()
        matched_lines = []
        for var_name, (pattern, nocase) in rule.strings.items():
            flags = re.IGNORECASE if nocase else 0
            for i, line in enumerate(lines):
                if re.search(re.escape(pattern), line, flags):
                    matched_vars.add(var_name)
                    matched_lines.append((i+1, line))
                    
        if evaluate_condition(rule.condition, matched_vars):
            line_num = matched_lines[0][0] if matched_lines else 1
            snippet = matched_lines[0][1] if matched_lines else ""
            findings.append({
                "id": rule.name,
                "category": "YARA Signature",
                "severity": rule.meta.get("severity", "HIGH"),
                "file": filepath,
                "line": line_num,
                "snippet": snippet.strip(),
                "description": rule.meta.get("description", "Pattern matched."),
                "confidence": 75
            })
            
    return findings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("rules", help="YARA rules file")
    parser.add_argument("file", help="File to scan")
    args = parser.parse_args()
    
    rules = load_rules(Path(args.rules))
    path = Path(args.file)
    if path.exists():
        findings = scan_content(path.read_text(), rules, str(path))
        print(json.dumps(findings, indent=2))

if __name__ == "__main__":
    main()
