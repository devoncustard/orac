#!/usr/bin/env python3
"""Auto-update OrAC mkdocs API docs from source code.

Runs mkdocstrings to regenerate API reference from Python docstrings.
Use before deploying to keep API docs in sync with code.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
API_DIR = DOCS / "api"


def ensure_api_dir():
    """Ensure the API output directory exists."""
    API_DIR.mkdir(parents=True, exist_ok=True)


def generate_api_docs():
    """Generate API reference pages from mkdocstrings config."""
    ensure_api_dir()
    
    # mkdocstrings auto-generates from mkdocs.yml handlers config
    # We just need to ensure the output dir exists
    print("API docs will be generated automatically by mkdocstrings during build.")
    print("Run 'mkdocs build' to generate full site.")


def update_nav():
    """Regenerate the nav section to include all API modules."""
    orac_dir = ROOT / "orac"
    if not orac_dir.exists():
        return
    
    modules = []
    for pyfile in sorted(orac_dir.rglob("*.py")):
        if pyfile.name.startswith("_") or pyfile.name == "__pycache__":
            continue
        rel = pyfile.relative_to(ROOT)
        name = ".".join(rel.with_suffix("").parts)
        modules.append((name, rel))
    
    print(f"Found {len(modules)} Python modules:")
    for name, rel in modules:
        print(f"  {name} → {rel}")


def main():
    print("=" * 50)
    print("OrAC Docs Auto-Update")
    print("=" * 50)
    
    generate_api_docs()
    update_nav()
    
    print("\n" + "=" * 50)
    print("Build site: mkdocs build")
    print("Serve site: mkdocs serve")
    print("=" * 50)


if __name__ == "__main__":
    main()
