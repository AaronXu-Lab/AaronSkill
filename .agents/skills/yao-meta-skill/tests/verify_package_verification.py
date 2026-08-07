#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tests" / "tmp_package_verification"
PACKAGER = ROOT / "scripts" / "cross_packager.py"
VERIFIER = ROOT / "scripts" / "verify_package.py"
EXPECTATIONS = ROOT / "evals" / "packaging_expectations.json"


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    payload = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "payload": payload,
    }


def build_package(out_dir: Path, skill_root: Path = ROOT) -> dict:
    return run(
        [
            sys.executable,
            str(PACKAGER),
            str(skill_root),
            "--platform",
            "openai",
            "--platform",
            "claude",
            "--platform",
            "generic",
            "--platform",
            "vscode",
            "--expectations",
            str(EXPECTATIONS),
            "--output-dir",
            str(out_dir),
            "--zip",
        ]
    )


def verify_package(out_dir: Path, output_json: Path, output_md: Path, skill_root: Path = ROOT) -> dict:
    return run(
        [
            sys.executable,
            str(VERIFIER),
            str(skill_root),
            "--package-dir",
            str(out_dir),
            "--expectations",
            str(EXPECTATIONS),
            "--registry-json",
            str(ROOT / "reports" / "registry_audit.json"),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--require-zip",
            "--generated-at",
            "2026-06-13",
        ]
    )


def verify_source_entrypoint_scan() -> None:
    with tempfile.TemporaryDirectory(prefix="source-entrypoint-scan-") as temp_root:
        root = Path(temp_root)
        (root / "SKILL.md").write_text("root\n", encoding="utf-8")
        (root / "examples" / "demo").mkdir(parents=True)
        (root / "examples" / "demo" / "SKILL.md").write_text("nested\n", encoding="utf-8")
        (root / ".agents" / "skills" / "local-helper").mkdir(parents=True)
        (root / ".agents" / "skills" / "local-helper" / "SKILL.md").write_text("local\n", encoding="utf-8")

        assert source_skill_entries(root) == [
            Path("SKILL.md"),
            Path("examples/demo/SKILL.md"),
        ]


def source_skill_entries(root: Path) -> list[Path]:
    entries = []
    for path in root.rglob("SKILL.md"):
        relative = path.relative_to(root)
        if relative.parts[0] in {".agents", ".git", "dist"}:
            continue
        if len(relative.parts) >= 2 and relative.parts[0] == "tests" and relative.parts[1].startswith("tmp"):
            continue
        entries.append(relative)
    return sorted(entries)


def main() -> None:
    verify_source_entrypoint_scan()
    source_entries = source_skill_entries(ROOT)
    assert source_entries == [Path("SKILL.md")], source_entries

    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True, exist_ok=True)

    valid_dir = TMP / "dist"
    build = build_package(valid_dir)
    assert build["ok"], build
    valid = verify_package(valid_dir, TMP / "package_verification.json", TMP / "package_verification.md")
    payload = valid["payload"]
    assert valid["ok"], valid
    assert payload["ok"], payload
    assert payload["summary"]["target_count"] == 4, payload
    assert payload["summary"]["adapter_count"] == 4, payload
    assert payload["summary"]["archive_present"], payload
    assert payload["summary"]["archive_sha256"], payload
    assert payload["summary"]["nested_skill_entry_count"] == 0, payload
    assert not payload["failures"], payload
    assert (TMP / "package_verification.md").exists(), TMP
    with zipfile.ZipFile(valid_dir / "yao-meta-skill.zip") as archive:
        skill_entries = sorted(name for name in archive.namelist() if name.endswith("/SKILL.md"))
    assert skill_entries == ["yao-meta-skill/SKILL.md"], skill_entries

    with tempfile.TemporaryDirectory(prefix="renamed-package-root-") as temp_root:
        renamed_root = Path(temp_root) / "checkout-alias"
        shutil.copytree(
            ROOT,
            renamed_root,
            ignore=shutil.ignore_patterns(".git", ".previews", "dist", "__pycache__", ".pytest_cache", "tmp*"),
        )
        renamed_dir = TMP / "renamed-dist"
        renamed_build = build_package(renamed_dir, renamed_root)
        assert renamed_build["ok"], renamed_build
        assert (renamed_dir / "yao-meta-skill.zip").exists(), renamed_build
        with zipfile.ZipFile(renamed_dir / "yao-meta-skill.zip") as archive:
            names = set(archive.namelist())
        assert "yao-meta-skill/SKILL.md" in names, sorted(list(names))[:10]
        assert not [name for name in names if name.endswith("/SKILL.md") and name != "yao-meta-skill/SKILL.md"], names
        renamed_valid = verify_package(renamed_dir, TMP / "renamed_package_verification.json", TMP / "renamed_package_verification.md", renamed_root)
        assert renamed_valid["ok"], renamed_valid

    nested_skill_dir = TMP / "nested-skill-dist"
    shutil.copytree(valid_dir, nested_skill_dir)
    with zipfile.ZipFile(nested_skill_dir / "yao-meta-skill.zip", "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("yao-meta-skill/examples/demo/SKILL.md", "---\nname: demo\n---\n")
    nested = verify_package(nested_skill_dir, TMP / "nested_skill.json", TMP / "nested_skill.md")
    assert nested["returncode"] == 2, nested
    nested_payload = nested["payload"]
    assert nested_payload["summary"]["nested_skill_entry_count"] == 1, nested_payload
    assert any("Archive exposes only the root SKILL.md entrypoint" in item for item in nested_payload["failures"]), nested_payload

    unsafe_dir = TMP / "unsafe-dist"
    shutil.copytree(valid_dir, unsafe_dir)
    with zipfile.ZipFile(unsafe_dir / "yao-meta-skill.zip", "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("../evil.txt", "bad")
    unsafe = verify_package(unsafe_dir, TMP / "unsafe.json", TMP / "unsafe.md")
    assert unsafe["returncode"] == 2, unsafe
    unsafe_payload = unsafe["payload"]
    assert not unsafe_payload["ok"], unsafe_payload
    assert any("Archive has no absolute or parent-traversal entries" in item for item in unsafe_payload["failures"]), unsafe_payload

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
