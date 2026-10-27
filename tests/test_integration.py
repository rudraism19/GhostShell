"""End-to-end integration test running a mock llama.cpp server and executing the REPL."""

from __future__ import annotations

import http.server
import json
import socket
import threading
import time
from unittest.mock import patch

import pytest
from rich.console import Console

from ghostshell.client import GemmaClient
from ghostshell.commands import CommandHandler
from ghostshell.config import GhostConfig
from ghostshell.engine import GemmaEngine
from ghostshell.ui import GhostUI
from main import run_repl


class _MockLlamaHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len)
        data = json.loads(body.decode("utf-8"))

        user_query = data["messages"][-1]["content"]
        response = {
            "model": "gemma-3-1b-it-Q4_K_M",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"👻 Spectral wisdom for: {user_query}. Check your boundary conditions!",
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 16,
                "total_tokens": 28,
            },
        }
        resp_bytes = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp_bytes)))
        self.end_headers()
        self.wfile.write(resp_bytes)

    def do_GET(self) -> None:
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture
def mock_server_port() -> int:
    """Find a free port on localhost for the test server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_end_to_end_gemma_integration(mock_server_port: int) -> None:
    """Test full cycle: REPL prompt -> GemmaClient -> local server -> Rich response render."""
    server = http.server.HTTPServer(("127.0.0.1", mock_server_port), _MockLlamaHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.1)

    try:
        endpoint = f"http://127.0.0.1:{mock_server_port}/v1/chat/completions"
        config = GhostConfig(
            startup_animation=False,
            model_endpoint=endpoint,
            model_name="gemma-3-1b-it",
        )
        console = Console(record=True, width=100)
        ui = GhostUI(console=console, config=config)
        client = GemmaClient(endpoint=endpoint, model_name=config.model_name)
        handler = CommandHandler(config=config, client=client)
        engine = GemmaEngine(client=client, config=config)

        # Simulate user inputs
        inputs = ["/status", "How do I fix off-by-one errors?", "/exit"]
        with patch.object(ui, "get_input", side_effect=inputs):
            exit_code = run_repl(ui, handler, engine)

        assert exit_code == 0
        output = console.export_text()
        assert "ONLINE" in output
        assert "THE GHOST SPEAKS" in output
        assert "Spectral wisdom for: How do I fix off-by-one errors?" in output
        assert "Total Tokens:" in output
        assert "28" in output
        assert "Farewell, mortal." in output

    finally:
        server.shutdown()
