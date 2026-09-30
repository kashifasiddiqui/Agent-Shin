import http.server
import socketserver
import threading
from pathlib import Path
from fagent.browser.verifier import BrowserVerifier
from fagent.schemas.graph import ProjectGraph
from fagent.schemas.project import ProjectInfo, Framework, Language, PackageManager


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress console logging during tests


def run_test_server(directory: Path, port: int):
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(directory), **kwargs)
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        httpd.serve_forever()


def test_browser_verifier_overflow_and_a11y(tmp_path):
    # Create HTML page with intentional overflow and a11y issues
    html_content = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Browser Test Page</title>
        <style>
            body { margin: 0; padding: 20px; font-family: sans-serif; }
            .overflow-box { width: 1600px; height: 50px; background: red; }
        </style>
    </head>
    <body>
        <h1>Browser Verification Suite</h1>
        <div class="overflow-box" id="huge-element">Overflow Box</div>
        <img src="logo.png">
        <button id="icon-btn"></button>
    </body>
    </html>
    """
    (tmp_path / "index.html").write_text(html_content, encoding="utf-8")

    port = 8765
    server_thread = threading.Thread(target=run_test_server, args=(tmp_path, port), daemon=True)
    server_thread.start()

    # Build mock ProjectGraph
    proj_info = ProjectInfo(
        name="test-web-app",
        root_path=str(tmp_path),
        framework=Framework.REACT,
        language=Language.TYPESCRIPT,
        package_manager=PackageManager.NPM,
    )
    graph = ProjectGraph(
        project=proj_info,
        routes=[],
        entry_routes=["/"],
        generated_at="2026-09-30T12:00:00Z",
    )

    verifier = BrowserVerifier(tmp_path, headless=True)
    findings, audit_data = verifier.run_browser_verification(
        graph,
        base_url=f"http://127.0.0.1:{port}",
        routes=["/"]
    )

    assert audit_data["total_screenshots"] >= 3  # mobile, tablet, desktop
    assert (tmp_path / ".fagent" / "screenshots").exists()

    finding_messages = [f.message for f in findings]

    # Verify horizontal overflow detection on mobile (width: 375px < 1600px)
    assert any("Horizontal overflow" in m for m in finding_messages)

    # Verify accessibility checks
    assert any("alt attribute" in m for m in finding_messages)
    assert any("accessible text or aria-label" in m for m in finding_messages)
