from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "azure-imagegen" / "scripts" / "image_gen.py"
SKILL_PATH = REPO_ROOT / "skills" / "azure-imagegen" / "SKILL.md"
OPENAI_YAML_PATH = REPO_ROOT / "skills" / "azure-imagegen" / "agents" / "openai.yaml"
PLUGIN_MANIFEST_PATH = REPO_ROOT / ".codex-plugin" / "plugin.json"
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _run_cli_with_env(*args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _write_png(path: Path) -> None:
    path.write_bytes(ONE_PIXEL_PNG)


def _run_generate(deployment: str, *args: str) -> subprocess.CompletedProcess[str]:
    return _run_cli(
        "generate",
        "--endpoint",
        "https://example.openai.azure.com",
        "--deployment",
        deployment,
        "--prompt",
        "smoke test",
        *args,
        "--dry-run",
    )


def _load_skill_frontmatter() -> dict:
    raw = SKILL_PATH.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    return yaml.safe_load(match.group(1))


def test_plugin_manifest_references_existing_assets() -> None:
    manifest = json.loads(PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["name"] == "azure-imagegen"
    assert re.match(r"^\d+\.\d+\.\d+$", manifest["version"])
    assert manifest["skills"] == "./skills/"

    interface = manifest["interface"]
    assert len(interface["defaultPrompt"]) == 3

    asset_keys = ["composerIcon", "logo"]
    asset_paths = [interface[key] for key in asset_keys] + interface["screenshots"]
    for rel_path in asset_paths:
        assert rel_path.startswith("./")
        assert (REPO_ROOT / rel_path.removeprefix("./")).is_file()


def test_skill_metadata_matches_plugin_packaging() -> None:
    frontmatter = _load_skill_frontmatter()
    openai_yaml = yaml.safe_load(OPENAI_YAML_PATH.read_text(encoding="utf-8"))
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert frontmatter["name"] == "azure-imagegen"
    assert "Generate, edit, and batch-create images" in frontmatter["description"]
    assert "$azure-imagegen" in openai_yaml["interface"]["default_prompt"]
    assert "gpt-image-1.5" not in skill_text


def test_generate_help_smoke() -> None:
    result = _run_cli("--help")

    assert result.returncode == 0
    assert "generate-batch" in result.stdout
    assert "edit" in result.stdout
    assert "postprocess-transparent" in result.stdout


def test_generate_dry_run_does_not_create_output_dir(tmp_path: Path) -> None:
    out_dir = tmp_path / "generated"

    result = _run_cli(
        "generate",
        "--endpoint",
        "https://example.openai.azure.com",
        "--deployment",
        "gpt-image-prod",
        "--prompt",
        "smoke test",
        "--out-dir",
        str(out_dir),
        "--dry-run",
    )

    assert result.returncode == 0, result.stderr
    assert not out_dir.exists()
    payload = json.loads(result.stdout)
    assert payload["endpoint"] == "/images/generations"


def test_edit_dry_run_does_not_create_output_dir(tmp_path: Path) -> None:
    image_path = tmp_path / "input.png"
    out_dir = tmp_path / "edited"
    _write_png(image_path)

    result = _run_cli(
        "edit",
        "--endpoint",
        "https://example.openai.azure.com",
        "--deployment",
        "gpt-image-prod",
        "--image",
        str(image_path),
        "--prompt",
        "change only the background",
        "--out-dir",
        str(out_dir),
        "--dry-run",
    )

    assert result.returncode == 0, result.stderr
    assert not out_dir.exists()
    payload = json.loads(result.stdout)
    assert payload["endpoint"] == "/images/edits"
    assert payload["image"] == [str(image_path)]


def test_generate_batch_dry_run_does_not_create_output_dir(tmp_path: Path) -> None:
    input_path = tmp_path / "jobs.jsonl"
    out_dir = tmp_path / "batch"
    input_path.write_text('{"prompt": "batch smoke test"}\n', encoding="utf-8")

    result = _run_cli(
        "generate-batch",
        "--endpoint",
        "https://example.openai.azure.com",
        "--deployment",
        "gpt-image-prod",
        "--input",
        str(input_path),
        "--out-dir",
        str(out_dir),
        "--dry-run",
    )

    assert result.returncode == 0, result.stderr
    assert not out_dir.exists()
    payload = json.loads(result.stdout)
    assert payload["endpoint"] == "/images/generations"
    assert payload["outputs"] == [str(out_dir / "001-batch-smoke-test.png")]


def test_gpt_image_2_omits_default_size_for_routing() -> None:
    result = _run_generate("gpt-image-2-prod")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["model"] == "gpt-image-2-prod"
    assert "size" not in payload


@pytest.mark.parametrize("size", ["3840x2160", "2160x3840", "1280x720"])
def test_gpt_image_2_accepts_4k_and_custom_aligned_sizes(size: str) -> None:
    result = _run_generate("gpt-image-2-prod", "--size", size)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["size"] == size


def test_gpt_image_2_rejects_too_small_size() -> None:
    result = _run_generate("gpt-image-2-prod", "--size", "800x800")

    assert result.returncode == 1
    assert "at least 655,360" in result.stderr


def test_gpt_image_2_rejects_unaligned_size() -> None:
    result = _run_generate("gpt-image-2-prod", "--size", "1025x1024")

    assert result.returncode == 1
    assert "multiple of 16" in result.stderr


def test_gpt_image_2_allows_over_budget_size_with_warning() -> None:
    result = _run_generate("gpt-image-2-prod", "--size", "3840x3840")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["size"] == "3840x3840"
    assert "Azure may resize the final image to fit" in result.stderr


def test_legacy_deployment_still_rejects_gpt_image_2_custom_size() -> None:
    result = _run_generate("gpt-image-prod", "--size", "3840x2160")

    assert result.returncode == 1
    assert "size must be one of" in result.stderr


def test_gpt_image_2_rejects_transparent_background() -> None:
    result = _run_generate(
        "gpt-image-2-prod",
        "--background",
        "transparent",
        "--output-format",
        "png",
    )

    assert result.returncode == 1
    assert "GPT-image-2 does not support background=transparent" in result.stderr
    assert "postprocess-transparent" in result.stderr


def test_legacy_deployment_accepts_transparent_background() -> None:
    result = _run_generate(
        "gpt-image-prod",
        "--background",
        "transparent",
        "--output-format",
        "png",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["background"] == "transparent"
    assert payload["output_format"] == "png"


def test_postprocess_transparent_dry_run_prints_magick_command(tmp_path: Path) -> None:
    image_path = tmp_path / "keyed.png"
    out_path = tmp_path / "transparent.png"
    _write_png(image_path)

    result = _run_cli(
        "postprocess-transparent",
        "--input",
        str(image_path),
        "--out",
        str(out_path),
        "--key-color",
        "#00FF00",
        "--trim",
        "--dry-run",
    )

    assert result.returncode == 0, result.stderr
    assert not out_path.exists()
    payload = json.loads(result.stdout)
    command = payload["command"]
    assert Path(command[0]).name.lower().startswith("magick")
    assert "-transparent" in command
    assert "#00FF00" in command
    assert "-trim" in command
    assert "+repage" in command


def test_postprocess_transparent_missing_magick_is_clear(tmp_path: Path) -> None:
    image_path = tmp_path / "keyed.png"
    out_path = tmp_path / "transparent.png"
    _write_png(image_path)
    env = {**os.environ, "PATH": ""}

    result = _run_cli_with_env(
        "postprocess-transparent",
        "--input",
        str(image_path),
        "--out",
        str(out_path),
        "--key-color",
        "#00FF00",
        env=env,
    )

    assert result.returncode == 1
    assert "ImageMagick `magick` was not found on PATH" in result.stderr


def test_postprocess_transparent_requires_png_output(tmp_path: Path) -> None:
    image_path = tmp_path / "keyed.png"
    _write_png(image_path)

    result = _run_cli(
        "postprocess-transparent",
        "--input",
        str(image_path),
        "--out",
        str(tmp_path / "transparent.jpg"),
        "--key-color",
        "#00FF00",
        "--dry-run",
    )

    assert result.returncode == 1
    assert "output must be a PNG" in result.stderr
