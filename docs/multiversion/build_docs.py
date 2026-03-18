#!/usr/bin/env python3
"""
Build ELD documentation for a specific branch using git worktrees.

This script creates git worktrees for both llvm-project and eld repositories,
configures a CMake build, and builds the eld-docs target. The resulting HTML
documentation is copied to the specified output directory.

Usage:
    build_version.py --branch <branch> --output-name <name> \
                     --eld-repo <path> --llvm-repo <path> \
                     --work-dir <path> --output-dir <path> \
                     [--llvm-branch <branch>]

Example:
    build_version.py --branch main --output-name latest \
                     --eld-repo /path/to/eld --llvm-repo /path/to/llvm-project \
                     --work-dir /tmp/docs-build --output-dir /tmp/site
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run(cmd: list, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and print it for visibility."""
    print(f"+ {' '.join(str(c) for c in cmd)}", flush=True)
    return subprocess.run(cmd, cwd=cwd, check=check)


def run_output(cmd: list, cwd: Optional[Path] = None) -> str:
    """Run a command and return its stdout."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def worktree_exists(repo_path: Path, worktree_path: Path) -> bool:
    """Check if a worktree already exists at the given path."""
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return str(worktree_path) in result.stdout
    except subprocess.CalledProcessError:
        return False


def create_worktree(repo_path: Path, worktree_path: Path, branch: str, detach: bool = True) -> None:
    """Create a git worktree for the specified branch (detached by default)."""
    run(["git", "worktree", "prune"], cwd=repo_path, check=False)
    
    if worktree_path.exists():
        if worktree_exists(repo_path, worktree_path):
            print(f"Worktree already exists: {worktree_path}")
            run(["git", "fetch", "origin", branch], cwd=worktree_path, check=False)
            run(["git", "checkout", "--detach", f"origin/{branch}"], cwd=worktree_path)
            return
        else:
            print(f"Removing stale directory: {worktree_path}")
            shutil.rmtree(worktree_path)

    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    
    run(["git", "fetch", "origin", branch], cwd=repo_path, check=False)
    run(["git", "worktree", "add", "--detach", str(worktree_path), f"origin/{branch}"], cwd=repo_path)


def remove_worktree(repo_path: Path, worktree_path: Path) -> None:
    """Remove a git worktree."""
    if worktree_exists(repo_path, worktree_path):
        run(["git", "worktree", "remove", str(worktree_path), "--force"],
            cwd=repo_path, check=False)
    elif worktree_path.exists():
        shutil.rmtree(worktree_path)


def find_ninja() -> str:
    """Find ninja or ninja-build executable."""
    for name in ["ninja", "ninja-build"]:
        if shutil.which(name):
            return name
    raise RuntimeError("ninja not found in PATH")


def build_docs(
    eld_branch: str,
    output_name: str,
    eld_repo: Path,
    llvm_repo: Path,
    work_dir: Path,
    output_dir: Path,
    llvm_branch: str = "main",
    version_label: Optional[str] = None,
    clean: bool = False,
) -> Path:
    """
    Build documentation for a specific ELD branch.

    Args:
        eld_branch: Git branch of ELD to build docs for
        output_name: Name for the output directory (e.g., 'latest', '22.x')
        eld_repo: Path to the ELD git repository
        llvm_repo: Path to the llvm-project git repository
        work_dir: Working directory for worktrees and builds
        output_dir: Output directory for the final HTML docs
        llvm_branch: LLVM branch to use (default: main)
        version_label: Human-readable version label (default: same as output_name)
        clean: If True, remove existing worktrees and rebuild from scratch

    Returns:
        Path to the output HTML directory
    """
    version_label = version_label or output_name

    # Paths
    llvm_worktree = work_dir / "_worktrees" / f"llvm-project-{output_name}"
    eld_worktree = llvm_worktree / "llvm" / "tools" / "eld"
    build_dir = work_dir / "_builds" / output_name

    print(f"\n{'=' * 70}")
    print(f"Building docs for ELD branch '{eld_branch}' -> '{output_name}'")
    print(f"  Version label: {version_label}")
    print(f"  LLVM branch: {llvm_branch}")
    print(f"  Work dir: {work_dir}")
    print(f"  Output dir: {output_dir}")
    print(f"{'=' * 70}\n")

    # Clean if requested
    if clean:
        print("Cleaning existing worktrees and build...")
        remove_worktree(llvm_repo, llvm_worktree)
        if build_dir.exists():
            shutil.rmtree(build_dir)

    # Step 1: Create LLVM worktree (detached to allow same branch in multiple worktrees)
    print("\n[Step 1/5] Creating LLVM worktree...")
    create_worktree(llvm_repo, llvm_worktree, llvm_branch, detach=True)

    # Step 2: Create ELD worktree inside LLVM (detached to avoid branch conflicts)
    print("\n[Step 2/5] Creating ELD worktree...")
    eld_tools_dir = llvm_worktree / "llvm" / "tools"
    eld_tools_dir.mkdir(parents=True, exist_ok=True)

    if eld_worktree.exists():
        if eld_worktree.is_symlink() or not worktree_exists(eld_repo, eld_worktree):
            print(f"Removing existing eld directory: {eld_worktree}")
            if eld_worktree.is_symlink():
                eld_worktree.unlink()
            else:
                shutil.rmtree(eld_worktree)

    create_worktree(eld_repo, eld_worktree, eld_branch, detach=True)

    # Step 3: Configure CMake
    print("\n[Step 3/5] Configuring CMake...")
    build_dir.mkdir(parents=True, exist_ok=True)

    cmake_args = [
        "cmake",
        "-G", "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DLLVM_ENABLE_SPHINX=ON",
        "-DLLVM_TARGETS_TO_BUILD=ARM;AArch64;RISCV;Hexagon",
        f"-DELD_DOC_VERSION_LABEL={version_label}",
        str(llvm_worktree / "llvm"),
    ]

    # Find compilers
    for compiler_var, names in [("CMAKE_C_COMPILER", ["clang", "gcc"]),
                                 ("CMAKE_CXX_COMPILER", ["clang++", "g++"])]:
        for name in names:
            path = shutil.which(name)
            if path:
                cmake_args.insert(-1, f"-D{compiler_var}={path}")
                break

    run(cmake_args, cwd=build_dir)

    # Step 4: Build eld-docs
    print("\n[Step 4/5] Building eld-docs...")
    ninja = find_ninja()
    run([ninja, "eld-docs"], cwd=build_dir)

    # Step 5: Copy output
    print("\n[Step 5/5] Copying output...")
    html_src = build_dir / "tools" / "eld" / "docs" / "userguide" / "html"
    html_dst = output_dir / output_name

    if not html_src.exists():
        raise RuntimeError(f"HTML output not found: {html_src}")

    if html_dst.exists():
        shutil.rmtree(html_dst)

    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(html_src, html_dst)

    print(f"\n{'=' * 70}")
    print(f"SUCCESS: Docs for '{output_name}' built at: {html_dst}")
    print(f"{'=' * 70}\n")

    return html_dst


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build ELD documentation for a specific branch using git worktrees",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--branch", required=True,
        help="ELD branch to build (e.g., 'main', 'release/22.x')"
    )
    parser.add_argument(
        "--output-name", required=True,
        help="Output directory name (e.g., 'latest', '22.x')"
    )
    parser.add_argument(
        "--eld-repo", required=True, type=Path,
        help="Path to ELD git repository"
    )
    parser.add_argument(
        "--llvm-repo", required=True, type=Path,
        help="Path to llvm-project git repository"
    )
    parser.add_argument(
        "--work-dir", required=True, type=Path,
        help="Working directory for worktrees and builds"
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path,
        help="Output directory for HTML docs"
    )
    parser.add_argument(
        "--llvm-branch", default="main",
        help="LLVM branch to use (default: main)"
    )
    parser.add_argument(
        "--version-label",
        help="Human-readable version label (default: same as output-name)"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Clean existing worktrees and rebuild from scratch"
    )

    args = parser.parse_args()

    try:
        build_docs(
            eld_branch=args.branch,
            output_name=args.output_name,
            eld_repo=args.eld_repo.resolve(),
            llvm_repo=args.llvm_repo.resolve(),
            work_dir=args.work_dir.resolve(),
            output_dir=args.output_dir.resolve(),
            llvm_branch=args.llvm_branch,
            version_label=args.version_label,
            clean=args.clean,
        )
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Command failed with exit code {e.returncode}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
