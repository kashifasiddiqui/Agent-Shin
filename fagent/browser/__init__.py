"""Browser agent and Playwright verification."""

from fagent.browser.launcher import BrowserLauncher
from fagent.browser.crawler import RouteCrawler
from fagent.browser.inspector import DOMInspector
from fagent.browser.verifier import BrowserVerifier

__all__ = [
    "BrowserLauncher",
    "RouteCrawler",
    "DOMInspector",
    "BrowserVerifier",
]
