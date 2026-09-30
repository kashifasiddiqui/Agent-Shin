from pathlib import Path
from typing import Dict, List, Set
from fagent.schemas.graph import AssetNode, AssetType


ASSET_EXTENSIONS: Dict[str, AssetType] = {
    ".png": AssetType.IMAGE,
    ".jpg": AssetType.IMAGE,
    ".jpeg": AssetType.IMAGE,
    ".webp": AssetType.IMAGE,
    ".avif": AssetType.IMAGE,
    ".gif": AssetType.IMAGE,
    ".ico": AssetType.IMAGE,
    ".svg": AssetType.SVG,
    ".woff": AssetType.FONT,
    ".woff2": AssetType.FONT,
    ".ttf": AssetType.FONT,
    ".eot": AssetType.FONT,
    ".otf": AssetType.FONT,
    ".mp4": AssetType.VIDEO,
    ".webm": AssetType.VIDEO,
    ".mp3": AssetType.AUDIO,
    ".wav": AssetType.AUDIO,
}


class AssetScanner:
    """Discovers assets in public and src directories and checks for references in code."""

    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()

    def scan_assets(self, search_dirs: List[Path], code_files: List[Path]) -> List[AssetNode]:
        assets: List[AssetNode] = []
        asset_map: Dict[str, AssetNode] = {}

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for path in search_dir.rglob("*"):
                if path.is_file() and path.suffix.lower() in ASSET_EXTENSIONS:
                    if any(ignored in path.parts for ignored in ["node_modules", "dist", ".fagent", ".git"]):
                        continue
                    rel_path = path.relative_to(self.root_path).as_posix()
                    node = AssetNode(
                        file_path=rel_path,
                        asset_type=ASSET_EXTENSIONS[path.suffix.lower()],
                        size_bytes=path.stat().st_size,
                        is_referenced=False,
                        referenced_by=[]
                    )
                    assets.append(node)
                    asset_map[path.name] = node

        # Check references in source code
        if asset_map and code_files:
            for code_file in code_files:
                try:
                    content = code_file.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue

                for filename, node in asset_map.items():
                    if filename in content:
                        rel_code = code_file.relative_to(self.root_path).as_posix()
                        if rel_code not in node.referenced_by:
                            node.is_referenced = True
                            node.referenced_by.append(rel_code)

        return sorted(assets, key=lambda a: a.file_path)
