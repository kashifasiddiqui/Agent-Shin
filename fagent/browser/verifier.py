import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from fagent.browser.launcher import BrowserLauncher
from fagent.browser.crawler import RouteCrawler
from fagent.core.state import StateManager
from fagent.schemas.finding import Finding, FindingCategory, Severity, FindingStatus
from fagent.schemas.graph import ProjectGraph


class BrowserVerifier:
    """Orchestrates browser execution, responsive audits, accessibility verification, and screenshot generation."""

    def __init__(self, project_root: Path, headless: bool = True):
        self.project_root = Path(project_root).resolve()
        self.headless = headless
        self.state = StateManager(self.project_root)
        self.screenshots_dir = self.state.fagent_dir / "screenshots"

    def run_browser_verification(
        self,
        graph: ProjectGraph,
        base_url: Optional[str] = None,
        routes: Optional[List[str]] = None,
    ) -> Tuple[List[Finding], Dict[str, Any]]:
        findings: List[Finding] = []
        url = base_url or BrowserLauncher.detect_dev_server_url()

        if not url:
            # Cannot reach a running server
            return [], {
                "status": "error",
                "message": "No running frontend dev server detected. Start your dev server (e.g. 'npm run dev') or specify --url.",
            }

        target_routes = routes or [r.path for r in graph.routes] or ["/"]
        audit_data: Dict[str, Any] = {
            "base_url": url,
            "routes_inspected": {},
            "total_screenshots": 0,
        }

        launcher = BrowserLauncher(headless=self.headless)
        with launcher as browser:
            crawler = RouteCrawler(browser, self.screenshots_dir)

            counter = 1
            for route in target_routes:
                res = crawler.crawl_route(url, route)
                audit_data["routes_inspected"][route] = res

                if res.get("status") == "failed":
                    findings.append(
                        Finding(
                            id=f"BROWSER-{counter:04d}",
                            category=FindingCategory.ARCHITECTURE,
                            severity=Severity.HIGH,
                            message=f"Failed to render route '{route}': {res.get('error')}",
                            route=route,
                            evidence={"error": res.get("error")},
                            fixable=False,
                            status=FindingStatus.DETECTED,
                        )
                    )
                    counter += 1
                    continue

                # 1. Evaluate Responsive Overflow Findings
                for vp_name, vp_data in res.get("viewports", {}).items():
                    audit_data["total_screenshots"] += 1
                    overflow = vp_data.get("overflow", {})
                    if overflow.get("has_overflow"):
                        delta = overflow.get("overflow_delta", 0)
                        offenders = overflow.get("offenders", [])
                        findings.append(
                            Finding(
                                id=f"RESP-{counter:04d}",
                                category=FindingCategory.RESPONSIVE,
                                severity=Severity.HIGH if delta > 50 else Severity.MEDIUM,
                                message=f"Horizontal overflow ({delta}px) on '{route}' at {vp_name} viewport ({vp_data.get('width')}px)",
                                route=route,
                                evidence={
                                    "viewport": vp_name,
                                    "viewport_width": vp_data.get("width"),
                                    "content_width": overflow.get("content_width"),
                                    "overflow_delta": delta,
                                    "offending_elements": offenders,
                                    "screenshot": vp_data.get("screenshot"),
                                },
                                fixable=False,
                                status=FindingStatus.DETECTED,
                            )
                        )
                        counter += 1

                # 2. Evaluate Accessibility Findings
                for issue in res.get("a11y_issues", []):
                    issue_type = issue.get("type", "")
                    sev = Severity.MEDIUM if issue_type in {"missing-alt", "empty-button"} else Severity.LOW
                    findings.append(
                        Finding(
                            id=f"A11Y-{counter:04d}",
                            category=FindingCategory.ACCESSIBILITY,
                            severity=sev,
                            message=f"{issue.get('message')} on route '{route}'",
                            route=route,
                            evidence=issue,
                            fixable=issue_type in {"missing-alt", "empty-button"},
                            status=FindingStatus.DETECTED,
                        )
                    )
                    counter += 1

        # Persist browser crawl metadata
        if self.state.is_initialized():
            report_target = self.state.fagent_dir / "browser-audit.json"
            self.state._save_json(report_target, audit_data)

        return findings, audit_data
