from importlib.metadata import metadata, version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_distribution_identity() -> None:
    assert version("diagrams") == "1.0.0"
    assert metadata("diagrams")["Name"] == "diagrams"
    assert "Repository, https://github.com/diagramflow/diagrams" in metadata("diagrams").get_all("Project-URL")


def test_snapshot_provenance_is_exact() -> None:
    text = (ROOT / "UPSTREAM.md").read_text(encoding="utf-8")
    assert "v0.25.1" in text
    assert "dd0763d939f377c99898951a489e813c0360cd4a" in text


def test_representative_resources_exist() -> None:
    for provider in ("aws", "azure", "gcp", "k8s"):
        assert (ROOT / "resources" / provider).is_dir()
