import socket
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright


class BrowserLauncher:
    """Manages launching Playwright Chromium instances and checking local dev servers."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    def start(self) -> Browser:
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        return self._browser

    def stop(self) -> None:
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @staticmethod
    def is_port_open(host: str = "localhost", port: int = 5173, timeout: float = 1.0) -> bool:
        """Checks if a local port is listening (e.g. Vite dev server on 5173 or 3000)."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            try:
                s.connect((host, port))
                return True
            except (socket.timeout, ConnectionRefusedError, OSError):
                return False

    @staticmethod
    def detect_dev_server_url(candidate_ports: Optional[list] = None) -> Optional[str]:
        """Detects if a common dev server port is currently running."""
        ports = candidate_ports or [5173, 3000, 8080, 5174, 4173]
        for port in ports:
            if BrowserLauncher.is_port_open(port=port):
                return f"http://localhost:{port}"
        return None
