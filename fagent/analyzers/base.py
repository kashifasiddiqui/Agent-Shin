from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from fagent.schemas.finding import Finding
from fagent.schemas.graph import ProjectGraph


class BaseAnalyzer(ABC):
    """Abstract base class for all FAgent analyzers."""

    @property
    @abstractmethod
    def category_name(self) -> str:
        """Name of the category inspected by this analyzer."""
        pass

    @abstractmethod
    def analyze(self, project_root: Path, graph: ProjectGraph) -> List[Finding]:
        """Runs deterministic analysis on the target project and returns findings."""
        pass
