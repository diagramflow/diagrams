import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat


Manifest = dict[str, Any]


def _load_manifest(path: Path) -> Manifest:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest is not valid JSON: {path}") from exc


def _image_path(manifest_path: Path, render: dict[str, object]) -> Path:
    return manifest_path.parent / str(render["path"])


def _mean_rgb_delta(baseline_path: Path, candidate_path: Path) -> float:
    with Image.open(baseline_path) as baseline_image:
        baseline = baseline_image.convert("RGB")
    with Image.open(candidate_path) as candidate_image:
        candidate = candidate_image.convert("RGB")

    diff = ImageChops.difference(baseline, candidate)
    channel_means = ImageStat.Stat(diff).mean[:3]
    return sum(channel_means) / len(channel_means)


def compare_manifests(
    baseline: Path,
    candidate: Path,
    max_mean_pixel_delta: float = 1.0,
) -> list[str]:
    baseline_manifest = _load_manifest(baseline)
    candidate_manifest = _load_manifest(candidate)
    errors: list[str] = []

    if baseline_manifest.get("public_api") != candidate_manifest.get("public_api"):
        errors.append("public_api mismatch")
    if baseline_manifest.get("resources") != candidate_manifest.get("resources"):
        errors.append("resources mismatch")

    baseline_renders = baseline_manifest.get("renders", {})
    candidate_renders = candidate_manifest.get("renders", {})
    baseline_cases = set(baseline_renders)
    candidate_cases = set(candidate_renders)

    for case in sorted(baseline_cases - candidate_cases):
        errors.append(f"candidate is missing case: {case}")
    for case in sorted(candidate_cases - baseline_cases):
        errors.append(f"candidate has extra case: {case}")

    for case in sorted(baseline_cases & candidate_cases):
        baseline_render = baseline_renders[case]
        candidate_render = candidate_renders[case]
        baseline_format = baseline_render.get("format")
        candidate_format = candidate_render.get("format")
        if baseline_format != candidate_format:
            errors.append(f"case {case} format mismatch: {baseline_format} != {candidate_format}")
            continue

        if baseline_format == "svg":
            if baseline_render.get("svg_sha256") != candidate_render.get("svg_sha256"):
                errors.append(f"case {case} svg_sha256 mismatch")
            continue

        baseline_size = (baseline_render.get("width"), baseline_render.get("height"))
        candidate_size = (candidate_render.get("width"), candidate_render.get("height"))
        if baseline_size != candidate_size:
            errors.append(
                "case "
                f"{case} dimensions mismatch: "
                f"{baseline_size[0]}x{baseline_size[1]} != {candidate_size[0]}x{candidate_size[1]}"
            )
            continue

        if baseline_format in {"png", "jpg", "jpeg"}:
            mean_delta = _mean_rgb_delta(_image_path(baseline, baseline_render), _image_path(candidate, candidate_render))
            if mean_delta > max_mean_pixel_delta:
                errors.append(
                    f"case {case} mean RGB delta {mean_delta:.2f} exceeds threshold {max_mean_pixel_delta:.2f}"
                )

    return errors


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Compare diagrams compatibility manifests.")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--max-mean-pixel-delta", type=float, default=1.0)
    args = parser.parse_args()

    errors = compare_manifests(args.baseline, args.candidate, args.max_mean_pixel_delta)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
