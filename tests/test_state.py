from fagent.core.state import StateManager
from fagent.scanner.project import ProjectScanner
from pathlib import Path


def test_state_manager_lifecycle(tmp_path):
    state = StateManager(tmp_path)
    assert not state.is_initialized()

    state.init_fagent()
    assert state.is_initialized()
    assert (tmp_path / ".fagent" / "config.json").exists()

    sample_root = Path(__file__).parent.parent / "examples" / "sample-react-app"
    scanner = ProjectScanner(sample_root)
    graph = scanner.scan()

    state.save_project_info(graph.project)
    state.save_graph(graph)

    loaded_proj = state.load_project_info()
    assert loaded_proj is not None
    assert loaded_proj.name == "sample-react-app"

    loaded_graph = state.load_graph()
    assert loaded_graph is not None
    assert len(loaded_graph.components) == len(graph.components)
    assert "Button" in loaded_graph.components
