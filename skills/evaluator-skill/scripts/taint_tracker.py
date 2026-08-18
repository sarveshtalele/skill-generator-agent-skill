from __future__ import annotations
import ast
import argparse
import json
from pathlib import Path
from dataclasses import dataclass
import sys

SOURCES = {
    'os.environ', 'os.getenv', 'open', 'sys.stdin', 'input', 
    'dotenv.load_dotenv', 'configparser'
}

SINKS = {
    'requests.post', 'requests.get', 'requests.put', 
    'urllib.request.urlopen', 'httpx.post', 'httpx.get',
    'subprocess.run', 'subprocess.call', 'subprocess.Popen',
    'os.system', 'os.popen', 'exec', 'eval', 
    'smtplib.SMTP.sendmail', 'socket.send', 'socket.connect'
}

@dataclass
class TaintFlow:
    source: str
    sink: str
    source_line: int
    sink_line: int
    path: list[str]
    confidence: int

class TaintTracker(ast.NodeVisitor):
    def __init__(self):
        self.tainted_vars = {} # var_name -> source info (source_name, line)
        self.flows: list[TaintFlow] = []

    def _get_call_name(self, node: ast.Call) -> str | None:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            curr = node.func
            while isinstance(curr, ast.Attribute):
                parts.insert(0, curr.attr)
                curr = curr.value
            if isinstance(curr, ast.Name):
                parts.insert(0, curr.id)
                return '.'.join(parts)
        return None

    def visit_Assign(self, node: ast.Assign):
        if isinstance(node.value, ast.Call):
            call_name = self._get_call_name(node.value)
            if call_name and any(call_name.startswith(s) for s in SOURCES):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.tainted_vars[target.id] = (call_name, node.lineno)
            
            # Check if calling a sink with a tainted var
            if call_name and any(call_name.startswith(s) for s in SINKS):
                for arg in node.value.args:
                    if isinstance(arg, ast.Name) and arg.id in self.tainted_vars:
                        src, src_line = self.tainted_vars[arg.id]
                        self.flows.append(TaintFlow(
                            source=src,
                            sink=call_name,
                            source_line=src_line,
                            sink_line=node.lineno,
                            path=[arg.id],
                            confidence=90
                        ))
        
        # Propagate taint
        if isinstance(node.value, ast.Name) and node.value.id in self.tainted_vars:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tainted_vars[target.id] = self.tainted_vars[node.value.id]

        self.generic_visit(node)
        
    def visit_Call(self, node: ast.Call):
        call_name = self._get_call_name(node)
        if call_name and any(call_name.startswith(s) for s in SINKS):
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id in self.tainted_vars:
                    src, src_line = self.tainted_vars[arg.id]
                    self.flows.append(TaintFlow(
                        source=src,
                        sink=call_name,
                        source_line=src_line,
                        sink_line=node.lineno,
                        path=[arg.id],
                        confidence=90
                    ))
        self.generic_visit(node)


def scan_file(filepath: str, text: str) -> list[dict]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    tracker = TaintTracker()
    tracker.visit(tree)
    
    findings = []
    lines = text.splitlines()
    
    for flow in tracker.flows:
        findings.append({
            "id": "TT1" if flow.source_line == flow.sink_line else "TT2",
            "category": "Security",
            "severity": "HIGH",
            "file": filepath,
            "line": flow.sink_line,
            "snippet": lines[flow.sink_line - 1] if 0 < flow.sink_line <= len(lines) else "",
            "description": f"Tainted data flows from {flow.source} (line {flow.source_line}) to {flow.sink}.",
            "confidence": flow.confidence
        })
        
    return findings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="File to scan")
    args = parser.parse_args()
    
    path = Path(args.file)
    if path.exists():
        text = path.read_text()
        findings = scan_file(str(path), text)
        print(json.dumps(findings, indent=2))

if __name__ == "__main__":
    main()
