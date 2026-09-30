import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from playwright.sync_api import Browser, Page
from fagent.browser.inspector import DOMInspector


STANDARD_VIEWPORTS = {
    "mobile": {"width": 375, "height": 667},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1440, "height": 900},
}


class RouteCrawler:
    """Visits application routes across responsive viewports, capturing DOM evidence and screenshots."""

    def __init__(self, browser: Browser, screenshots_dir: Path):
        self.browser = browser
        self.screenshots_dir = screenshots_dir.resolve()
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def crawl_route(self, base_url: str, route_path: str) -> Dict[str, Any]:
        """Inspects a single route across all standard viewports."""
        url = base_url.rstrip("/") + ("/" if not route_path.startswith("/") else "") + route_path.lstrip("/")
        route_slug = "root" if route_path in {"", "/"} else re.sub(r"[^a-zA-Z0-9_-]", "_", route_path.strip("/"))

        context = self.browser.new_context()
        page = context.new_page()

        route_result: Dict[str, Any] = {
            "route": route_path,
            "url": url,
            "viewports": {},
            "a11y_issues": [],
            "console_errors": [],
            "status": "success",
        }

        # Track console errors
        page.on("console", lambda msg: route_result["console_errors"].append(msg.text) if msg.type == "error" else None)

        try:
            # Navigate to target page
            page.goto(url, wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(500)  # Allow client-side rendering / animations to settle
        except Exception as e:
            route_result["status"] = "failed"
            route_result["error"] = str(e)
            context.close()
            return route_result

        # Run accessibility audit once at desktop
        try:
            a11y_data = page.evaluate(DOMInspector.CHECK_A11Y_SCRIPT)
            route_result["a11y_issues"] = a11y_data
        except Exception:
            pass

        # Inspect and screenshot each viewport
        for vp_name, vp_size in STANDARD_VIEWPORTS.items():
            try:
                page.set_viewport_size(vp_size)
                page.wait_for_timeout(300)

                # Check horizontal overflow
                overflow_data = page.evaluate(DOMInspector.CHECK_OVERFLOW_SCRIPT)

                # Capture full screenshot
                screenshot_filename = f"{route_slug}_{vp_name}.png"
                screenshot_path = self.screenshots_dir / screenshot_filename
                page.screenshot(path=str(screenshot_path), full_page=False)

                route_result["viewports"][vp_name] = {
                    "width": vp_size["width"],
                    "height": vp_size["height"],
                    "screenshot": screenshot_path.as_posix(),
                    "overflow": overflow_data,
                }
            except Exception as vp_err:
                route_result["viewports"][vp_name] = {"error": str(vp_err)}

        context.close()
        return route_result
