from pathlib import Path
from typer.testing import CliRunner
from fagent.cli import app
from fagent import __version__

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.stdout
    assert "scan" in result.stdout
    assert "status" in result.stdout


def test_cli_init_and_status(tmp_path):
    # Test init in temporary directory
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".fagent").exists()
    assert (tmp_path / ".fagent" / "config.json").exists()

    # Re-init should inform that it is already initialized
    result2 = runner.invoke(app, ["init", str(tmp_path)])
    assert result2.exit_code == 0
    assert "already initialized" in result2.stdout

    # Status before scan
    result_status = runner.invoke(app, ["status", str(tmp_path)])
    assert result_status.exit_code == 0
    assert "has not been scanned yet" in result_status.stdout


def test_cli_scan_sample_app():
    sample_root = Path(__file__).parent.parent / "examples" / "sample-react-app"
    result = runner.invoke(app, ["scan", str(sample_root)])
    assert result.exit_code == 0
    assert "Project Identity" in result.stdout
    assert "sample-react-app" in result.stdout
    assert "React" in result.stdout

    # Status after scan
    result_status = runner.invoke(app, ["status", str(sample_root)])
    assert result_status.exit_code == 0
    assert "sample-react-app" in result_status.stdout
    assert "Components:" in result_status.stdout


def test_cli_target_not_found():
    result = runner.invoke(app, ["scan", "non_existent_folder_xyz_123"])
    assert result.exit_code == 1
    assert "does not exist" in result.stdout
