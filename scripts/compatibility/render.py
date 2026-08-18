import hashlib
import importlib.util
import inspect
import json
import pkgutil
import re
import time
import xml.etree.ElementTree as ET
from importlib import import_module
from importlib.metadata import version
from pathlib import Path
from typing import Callable

from PIL import Image

import diagrams

RenderFunc = Callable[[Path, str], Path]


def _load_cases() -> dict[str, RenderFunc]:
    corpus_path = Path(__file__).resolve().parents[2] / "tests" / "compatibility" / "corpus.py"
    spec = importlib.util.spec_from_file_location("diagrams_compatibility_corpus", corpus_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load compatibility corpus: {corpus_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CASES


def _normalise_svg(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'(?<=")[^"]*/resources/', "$DIAGRAMS_ROOT/resources/", text)
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=False))
    root = ET.fromstring(text, parser=parser)
    for element in root.iter():
        if element.attrib:
            sorted_attributes = dict(sorted(element.attrib.items()))
            element.attrib.clear()
            element.attrib.update(sorted_attributes)
    return ET.tostring(root, encoding="utf-8")


def _public_api_inventory() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for module_info in pkgutil.walk_packages(diagrams.__path__, prefix=f"{diagrams.__name__}."):
        module = import_module(module_info.name)
        for class_name, value in inspect.getmembers(module, inspect.isclass):
            if class_name.startswith("_"):
                continue
            if value.__module__ != module_info.name:
                continue
            rows.append({"module": module_info.name, "class": class_name})
    return sorted(rows, key=lambda row: (row["module"], row["class"]))


def _resource_inventory() -> list[str]:
    package_root = Path(diagrams.__file__).resolve().parents[1]
    resources_root = package_root / "resources"
    return sorted(
        str(path.relative_to(resources_root))
        for path in resources_root.rglob("*")
        if path.is_file()
    )


def _render_case(output_dir: Path, case_name: str, render_func: RenderFunc, outformat: str) -> dict[str, object]:
    filename = output_dir / f"{case_name}"
    start = time.perf_counter()
    output_path = render_func(filename, outformat)
    duration_ms = int((time.perf_counter() - start) * 1000)
    relative_path = output_path.relative_to(output_dir)

    result: dict[str, object] = {
        "path": str(relative_path),
        "format": outformat,
        "duration_ms": duration_ms,
    }
    if outformat == "svg":
        result["svg_sha256"] = hashlib.sha256(_normalise_svg(output_path)).hexdigest()
    else:
        with Image.open(output_path) as image:
            result["width"] = image.width
            result["height"] = image.height
    return result


def render_corpus(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    renders: dict[str, dict[str, object]] = {}
    for case_name, render_func in _load_cases().items():
        for outformat in ("png", "jpg", "svg"):
            renders[f"{case_name}:{outformat}"] = _render_case(output_dir, case_name, render_func, outformat)

    return {
        "distribution_version": version("diagrams"),
        "public_api": _public_api_inventory(),
        "resources": _resource_inventory(),
        "renders": renders,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Render the diagrams compatibility corpus.")
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    manifest = render_corpus(args.output_dir)
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
