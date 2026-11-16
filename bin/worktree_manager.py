#!/usr/bin/env python3
"""
Multi-Agent Git Worktree Workspace Isolation for Hyper Agents Force.

Enables conflict-free parallel execution across collaborative teammates.
Assigns isolated branches and worktrees (.worktrees/<task_id>) per claimed task,
with automatic directory sandbox fallback (.sandboxes/<task_id>) in non-git environments.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_WORKTREE_ROOT = WORKSPACE_DIR / ".worktrees"
DEFAULT_SANDBOX_ROOT = WORKSPACE_DIR / ".sandboxes"


class WorktreeManager:
    """Manages isolated developer workspaces for teammate agents."""

    @classmethod
    def is_git_repo(cls, root_dir: Optional[Path] = None) -> bool:
        """Checks if directory has a functional git repository with at least one commit."""
        root = Path(root_dir or WORKSPACE_DIR).resolve()
        git_dir = root / ".git"
        if not git_dir.exists():
            return False
        try:
            res = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=str(root), capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

    @classmethod
    def create_worktree(
        cls,
        task_id: str,
        team_id: str = "default",
        agent_name: str = "agent",
        root_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Creates an isolated git worktree or filesystem sandbox for an agent task."""
        root = Path(root_dir or WORKSPACE_DIR).resolve()
        branch_name = f"agent/{team_id}/{task_id}"

        if cls.is_git_repo(root):
            wt_path = root / ".worktrees" / task_id
            wt_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if branch exists
            subprocess.run(["git", "branch", "-D", branch_name], cwd=str(root), capture_output=True)

            res = subprocess.run(
                ["git", "worktree", "add", "-b", branch_name, str(wt_path)],
                cwd=str(root),
                capture_output=True,
                text=True
            )

            if res.returncode == 0:
                return {
                    "task_id": task_id,
                    "team_id": team_id,
                    "agent": agent_name,
                    "mode": "GIT_WORKTREE",
                    "path": str(wt_path),
                    "branch": branch_name,
                    "status": "READY",
                }

        # Fallback: Filesystem Sandbox
        sb_path = root / ".sandboxes" / task_id
        if sb_path.exists():
            shutil.rmtree(sb_path, ignore_errors=True)
        sb_path.mkdir(parents=True, exist_ok=True)

        # Copy essential files (excluding ignored heavy dirs)
        ignored = {".git", "node_modules", ".venv", "venv", "__pycache__", ".agent", ".worktrees", ".sandboxes"}
        for item in root.iterdir():
            if item.name not in ignored:
                target = sb_path / item.name
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target)

        return {
            "task_id": task_id,
            "team_id": team_id,
            "agent": agent_name,
            "mode": "DIRECTORY_SANDBOX",
            "path": str(sb_path),
            "branch": branch_name,
            "status": "READY",
        }

    @classmethod
    def diff_worktree(cls, task_id: str, root_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Generates unified diff between the worktree/sandbox and the main workspace."""
        root = Path(root_dir or WORKSPACE_DIR).resolve()
        wt_path = root / ".worktrees" / task_id
        sb_path = root / ".sandboxes" / task_id

        if wt_path.exists() and cls.is_git_repo(root):
            res = subprocess.run(["git", "diff", "HEAD"], cwd=str(wt_path), capture_output=True, text=True)
            return {
                "task_id": task_id,
                "mode": "GIT_WORKTREE",
                "diff": res.stdout or "No uncommitted modifications in worktree.",
            }

        if sb_path.exists():
            diff_lines = []
            for item in sb_path.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(sb_path)
                    orig = root / rel
                    if not orig.exists():
                        diff_lines.append(f"[NEW FILE] {rel}")
                    else:
                        try:
                            t1 = orig.read_text(encoding="utf-8", errors="ignore")
                            t2 = item.read_text(encoding="utf-8", errors="ignore")
                            if t1 != t2:
                                diff_lines.append(f"[MODIFIED] {rel}")
                        except Exception:
                            pass
            return {
                "task_id": task_id,
                "mode": "DIRECTORY_SANDBOX",
                "diff": "\n".join(diff_lines) or "No modified files detected.",
            }

        return {"task_id": task_id, "error": "Worktree or sandbox not found.", "diff": ""}

    @classmethod
    def merge_worktree(cls, task_id: str, root_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Merges changes from the worktree/sandbox back into the main workspace."""
        root = Path(root_dir or WORKSPACE_DIR).resolve()
        wt_path = root / ".worktrees" / task_id
        sb_path = root / ".sandboxes" / task_id

        if wt_path.exists() and cls.is_git_repo(root):
            # Check commit in worktree
            subprocess.run(["git", "add", "."], cwd=str(wt_path), capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Completed task {task_id}"], cwd=str(wt_path), capture_output=True)

            # Merge branch in main
            branch = f"agent/*/{task_id}"
            res = subprocess.run(["git", "merge", branch], cwd=str(root), capture_output=True, text=True)
            return {
                "task_id": task_id,
                "status": "MERGED" if res.returncode == 0 else "MERGE_FAILED",
                "output": res.stdout or res.stderr,
            }

        if sb_path.exists():
            copied = []
            for item in sb_path.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(sb_path)
                    dest = root / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
                    copied.append(str(rel))
            return {
                "task_id": task_id,
                "status": "MERGED",
                "files_updated": copied,
            }

        return {"task_id": task_id, "status": "NOT_FOUND"}

    @classmethod
    def cleanup_worktree(cls, task_id: str, root_dir: Optional[Path] = None) -> bool:
        """Deletes worktree/sandbox and branch cleanly."""
        root = Path(root_dir or WORKSPACE_DIR).resolve()
        wt_path = root / ".worktrees" / task_id
        sb_path = root / ".sandboxes" / task_id

        if wt_path.exists() and cls.is_git_repo(root):
            subprocess.run(["git", "worktree", "remove", str(wt_path), "--force"], cwd=str(root), capture_output=True)
            return True

        if sb_path.exists():
            shutil.rmtree(sb_path, ignore_errors=True)
            return True

        return False

    @classmethod
    def list_active(cls, root_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Lists all active isolated worktrees and sandboxes."""
        root = Path(root_dir or WORKSPACE_DIR).resolve()
        active = []

        wt_root = root / ".worktrees"
        if wt_root.exists():
            for d in wt_root.iterdir():
                if d.is_dir():
                    active.append({"task_id": d.name, "mode": "GIT_WORKTREE", "path": str(d)})

        sb_root = root / ".sandboxes"
        if sb_root.exists():
            for d in sb_root.iterdir():
                if d.is_dir():
                    active.append({"task_id": d.name, "mode": "DIRECTORY_SANDBOX", "path": str(d)})

        return active


def main():
    if len(sys.argv) < 2:
        print("Usage: python worktree_manager.py [list|create <task_id>|diff <task_id>|merge <task_id>|cleanup <task_id>]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "list":
        active = WorktreeManager.list_active()
        print(f"\nActive Worktrees & Sandboxes ({len(active)}):")
        for item in active:
            print(f"- [{item['mode']}] Task: {item['task_id']} (Path: {item['path']})")
        print()
    elif cmd == "create":
        tid = sys.argv[2] if len(sys.argv) > 2 else "task-test-001"
        res = WorktreeManager.create_worktree(task_id=tid)
        print(f"\nCreated Workspace Isolation:")
        print(f"- Task: {res['task_id']}")
        print(f"- Mode: {res['mode']}")
        print(f"- Path: {res['path']}\n")
    elif cmd == "diff":
        tid = sys.argv[2] if len(sys.argv) > 2 else "task-test-001"
        res = WorktreeManager.diff_worktree(task_id=tid)
        print(f"\nDiff for Task [{tid}]:\n{res['diff']}\n")
    elif cmd == "cleanup":
        tid = sys.argv[2] if len(sys.argv) > 2 else "task-test-001"
        ok = WorktreeManager.cleanup_worktree(task_id=tid)
        print(f"\nCleanup Task [{tid}]: {'SUCCESS' if ok else 'NOT_FOUND'}\n")


if __name__ == "__main__":
    main()
