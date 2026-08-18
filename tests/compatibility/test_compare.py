import json
import struct
import zlib
from pathlib import Path

from scripts.compatibility.compare import compare_manifests


def _write_png(path: Path, width: int, height: int, rgb: tuple[int, int, int]) -> None:
    raw_rows = []
    row = bytes(rgb) * width
    for _ in range(height):
        raw_rows.append(b"\x00" + row)
    raw = b"".join(raw_rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)

    data = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(raw)),
            chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(data)


def valid_png_case(path: str = "core.png", width: int = 1, height: int = 1) -> dict[str, object]:
    return {
        "path": path,
        "format": "png",
        "width": width,
        "height": height,
        "duration_ms": 10,
    }


def valid_svg_case(svg_sha256: str = "a" * 64) -> dict[str, object]:
    return {
        "path": "core.svg",
        "format": "svg",
        "svg_sha256": svg_sha256,
        "duration_ms": 10,
    }


def write_manifest(root: Path, cases: dict[str, dict[str, object]]) -> Path:
    root.mkdir(parents=True)
    for case in cases.values():
        case_path = root / str(case["path"])
        case_path.parent.mkdir(parents=True, exist_ok=True)
        if case["format"] == "png":
            _write_png(
                case_path,
                int(case["width"]),
                int(case["height"]),
                tuple(case.get("rgb", (12, 34, 56))),  # type: ignore[arg-type]
            )
        else:
            case_path.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\" />", encoding="utf-8")

    manifest = {
        "distribution_version": "test",
        "public_api": [{"module": "diagrams.aws.compute", "class": "EC2"}],
        "resources": ["aws/compute/ec2.png"],
        "renders": cases,
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def test_compare_accepts_identical_manifests(tmp_path: Path) -> None:
    baseline = write_manifest(tmp_path / "baseline", {"core_png": valid_png_case()})
    candidate = write_manifest(tmp_path / "candidate", {"core_png": valid_png_case()})

    assert compare_manifests(baseline, candidate) == []


def test_compare_rejects_missing_case(tmp_path: Path) -> None:
    baseline = write_manifest(tmp_path / "baseline", {"core_png": valid_png_case()})
    candidate = write_manifest(tmp_path / "candidate", {})

    assert compare_manifests(baseline, candidate) == ["candidate is missing case: core_png"]


def test_compare_rejects_extra_case(tmp_path: Path) -> None:
    baseline = write_manifest(tmp_path / "baseline", {})
    candidate = write_manifest(tmp_path / "candidate", {"core_png": valid_png_case()})

    assert compare_manifests(baseline, candidate) == ["candidate has extra case: core_png"]


def test_compare_rejects_svg_digest_mismatch(tmp_path: Path) -> None:
    baseline = write_manifest(tmp_path / "baseline", {"core_svg": valid_svg_case("a" * 64)})
    candidate = write_manifest(tmp_path / "candidate", {"core_svg": valid_svg_case("b" * 64)})

    assert compare_manifests(baseline, candidate) == ["case core_svg svg_sha256 mismatch"]


def test_compare_rejects_raster_dimension_mismatch(tmp_path: Path) -> None:
    baseline = write_manifest(tmp_path / "baseline", {"core_png": valid_png_case(width=1, height=1)})
    candidate = write_manifest(tmp_path / "candidate", {"core_png": valid_png_case(width=2, height=1)})

    assert compare_manifests(baseline, candidate) == ["case core_png dimensions mismatch: 1x1 != 2x1"]


def test_compare_rejects_raster_mean_rgb_delta_above_threshold(tmp_path: Path) -> None:
    baseline_case = valid_png_case()
    baseline_case["rgb"] = (10, 10, 10)
    candidate_case = valid_png_case()
    candidate_case["rgb"] = (20, 20, 20)
    baseline = write_manifest(tmp_path / "baseline", {"core_png": baseline_case})
    candidate = write_manifest(tmp_path / "candidate", {"core_png": candidate_case})

    assert compare_manifests(baseline, candidate) == [
        "case core_png mean RGB delta 10.00 exceeds threshold 1.00"
    ]
