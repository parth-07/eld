#!/usr/bin/env python3
"""
Assemble multi-version ELD documentation site.

Creates the landing page (index.html), version manifest (versions.json),
and stable symlink for the multi-version documentation site.

Usage:
    assemble_site.py --site-dir <path> --versions '<json>'

Example:
    assemble_site.py --site-dir ./site \
        --versions '[{"path":"latest","label":"Latest (main)","dev":true},
                     {"path":"22.x","label":"Release 22.x","stable":true}]'
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"


def load_template(name: str) -> str:
    """Load a template file from the templates directory."""
    template_path = TEMPLATES_DIR / name
    return template_path.read_text()


def find_stable_version(versions: list[dict[str, Any]]) -> str | None:
    """Find the version marked as stable in the versions list."""
    for v in versions:
        if v.get("stable"):
            return v["path"]
    return None


def generate_index_html(versions: list[dict[str, Any]], output_path: Path) -> None:
    """Generate the landing page HTML with version links."""
    index_template = load_template("index.html")
    version_link_template = load_template("version_link.html")

    version_links = []
    for v in versions:
        badge = ""
        if v.get("stable"):
            badge = '\n                        <span class="badge badge-stable">stable</span>'
        elif v.get("dev"):
            badge = '\n                        <span class="badge badge-dev">dev</span>'

        version_links.append(version_link_template.format(
            path=v["path"],
            label=v["label"],
            badge=badge,
        ))

    html = index_template.format(version_links="".join(version_links))
    output_path.write_text(html)
    print(f"Generated: {output_path}")


def generate_versions_json(versions: list[dict[str, Any]], stable: str | None, output_path: Path) -> None:
    """Generate the versions manifest JSON file."""
    manifest = {
        "versions": versions,
        "stable": stable,
        "default": "stable" if stable else versions[0]["path"] if versions else None,
    }
    output_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Generated: {output_path}")


def create_stable_symlink(site_dir: Path, stable_target: str) -> None:
    """Create the 'stable' symlink pointing to the stable version directory."""
    stable_link = site_dir / "stable"

    if stable_link.is_symlink():
        stable_link.unlink()
    elif stable_link.exists():
        raise RuntimeError(f"'stable' exists but is not a symlink: {stable_link}")

    target_dir = site_dir / stable_target
    if not target_dir.exists():
        print(f"WARNING: Target directory does not exist yet: {target_dir}")

    os.symlink(stable_target, stable_link)
    print(f"Created symlink: stable -> {stable_target}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble multi-version ELD documentation site",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--site-dir", required=True, type=Path,
        help="Site output directory containing version subdirectories"
    )
    parser.add_argument(
        "--versions", required=True,
        help="JSON array of version specs: [{\"path\":\"...\",\"label\":\"...\",\"stable\":true}]"
    )

    args = parser.parse_args()

    try:
        site_dir = args.site_dir.resolve()
        versions = json.loads(args.versions)

        if not isinstance(versions, list):
            raise ValueError("--versions must be a JSON array")

        stable = find_stable_version(versions)

        site_dir.mkdir(parents=True, exist_ok=True)

        generate_index_html(versions, site_dir / "index.html")
        generate_versions_json(versions, stable, site_dir / "versions.json")

        if stable:
            create_stable_symlink(site_dir, stable)
        else:
            print("WARNING: No version marked as stable, skipping stable symlink")

        nojekyll = site_dir / ".nojekyll"
        nojekyll.touch()
        print(f"Created: {nojekyll}")

        print(f"\nSite assembled successfully: {site_dir}")
        return 0

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in --versions: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
