"""Serves the eval viewer with embedded evaluation data.
Scans workspace for outputs, embeds as base64 data URIs,
and serves viewer.html with injected data."""

from __future__ import annotations
import argparse
import base64
import http.server
import json
import os
import sys
from pathlib import Path

def collect_eval_data(workspace: Path) -> dict:
    """Scans workspace for:
    - outputs/ directory (text files, images)
    - grading.json, comparison.json, benchmark.json
    Returns structured dict for injection into viewer."""
    data = {"outputs": [], "benchmark": {}}
    
    # Load benchmark if exists
    bench_file = workspace / "benchmark.json"
    if bench_file.exists():
        try:
            data["benchmark"] = json.loads(bench_file.read_text())
        except Exception as e:
            print(f"Warning: Failed to load benchmark.json: {e}")

    # Load outputs and grades
    outputs_dir = workspace / "outputs"
    grading_file = workspace / "grading.json"
    feedback_file = workspace / "feedback.json"
    
    grades = {}
    if grading_file.exists():
        try:
            grades = json.loads(grading_file.read_text())
        except Exception:
            pass
            
    feedback = {}
    if feedback_file.exists():
        try:
            feedback = json.loads(feedback_file.read_text())
        except Exception:
            pass

    if outputs_dir.exists() and outputs_dir.is_dir():
        for path in sorted(outputs_dir.glob("*.txt")):
            case_id = path.stem
            content = path.read_text(errors="replace")
            item = {
                "id": case_id,
                "prompt": f"Prompt for {case_id} (mock or loaded)",
                "output": content,
                "passed": grades.get(case_id, {}).get("passed", False),
                "feedback": feedback.get(case_id, "")
            }
            # Check for image
            img_path = path.with_suffix(".png")
            if img_path.exists():
                b64 = base64.b64encode(img_path.read_bytes()).decode('ascii')
                item["image"] = f"data:image/png;base64,{b64}"
            data["outputs"].append(item)
            
    return data

def inject_data_into_viewer(viewer_html: str, data: dict) -> str:
    """Replaces window.__EVAL_DATA__ = {} placeholder with actual data."""
    data_json = json.dumps(data)
    target = "window.__EVAL_DATA__ = {};"
    replacement = f"window.__EVAL_DATA__ = {data_json};"
    return viewer_html.replace(target, replacement)

class ReviewHandler(http.server.SimpleHTTPRequestHandler):
    """Handles /api/feedback POST endpoint and serves injected HTML."""
    workspace: Path
    viewer_html_content: str

    def do_GET(self):
        if self.path == '/' or self.path == '/viewer.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.viewer_html_content.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/feedback':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                feedback_req = json.loads(body)
                case_id = feedback_req.get('caseId')
                feedback_text = feedback_req.get('feedback', '')
                
                feedback_path = self.workspace / 'feedback.json'
                existing = {}
                if feedback_path.exists():
                    existing = json.loads(feedback_path.read_text())
                
                existing[case_id] = feedback_text
                feedback_path.write_text(json.dumps(existing, indent=2))
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "saved"}')
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}" }}'.encode())
        else:
            self.send_error(404)

def serve_review(workspace: Path, port: int = 8765):
    """Starts HTTP server with eval data."""
    script_dir = Path(__file__).parent
    viewer_path = script_dir / "viewer.html"
    
    if not viewer_path.exists():
        print(f"Error: {viewer_path} not found.")
        sys.exit(1)
        
    viewer_html = viewer_path.read_text()
    data = collect_eval_data(workspace)
    injected_html = inject_data_into_viewer(viewer_html, data)
    
    # Custom handler setup
    class Handler(ReviewHandler):
        def __init__(self, *args, **kwargs):
            self.workspace = workspace
            self.viewer_html_content = injected_html
            super().__init__(*args, directory=str(workspace), **kwargs)
            
    server = http.server.HTTPServer(('', port), Handler)
    print(f"Serving eval viewer at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()

def main():
    parser = argparse.ArgumentParser(description="Serve the eval viewer.")
    parser.add_argument('--workspace', required=True, help="Path to evaluation workspace")
    parser.add_argument('--port', type=int, default=8765, help="Port to serve on")
    args = parser.parse_args()
    serve_review(Path(args.workspace), args.port)

if __name__ == "__main__":
    main()
