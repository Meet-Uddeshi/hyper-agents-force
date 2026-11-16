"""
Installer Engine for Meet AI Agents.

Handles deployment across levels and platforms:
  - Levels:
    * Project level (-p): Deploys into target project root.
    * User level (-u): Deploys to user profile (~/.gemini/).
    * Global level (-g): Deploys to system-wide global directory.
  - Platforms:
    * --cursor: Deploys Cursor rules (.cursorrules, .cursor/rules/*.mdc, .cursor/mcp.json).
    * --claude: Deploys Claude Code instructions (CLAUDE.md, .mcp.json).
    * --copilot: Deploys GitHub Copilot instructions (.github/copilot-instructions.md).
    * --codex: Deploys OpenAI Codex instructions (.codex/instructions.md).
    * --gemini / --antigravity: Deploys Gemini/Antigravity rules (GEMINI.md).
    * --all: Deploys all platform adapters into the destination.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

PACKAGE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = PACKAGE_DIR.parent
SOURCE_AGENT_DIR = WORKSPACE_DIR / ".agent"
SOURCE_GEMINI_MD = WORKSPACE_DIR / "GEMINI.md"
SOURCE_ENV_EXAMPLE = WORKSPACE_DIR / ".env.example"
SOURCE_GLOBAL_RULES = WORKSPACE_DIR / "global-rules"
SOURCE_PLATFORMS_DIR = WORKSPACE_DIR / "platforms"


class Installer:
    """Manages multi-level and multi-platform deployment of Meet AI Agents."""

    SUPPORTED_PLATFORMS = [
        "gemini",
        "antigravity",
        "claude",
        "cursor",
        "copilot",
        "codex",
        "all",
    ]

    @staticmethod
    def get_user_dir() -> Path:
        """Returns the user-level Antigravity directory."""
        home = Path.home()
        return home / ".gemini"

    @staticmethod
    def get_global_dir() -> Path:
        """Returns the system-level global directory."""
        if os.name == "nt":
            all_users = os.environ.get("ALLUSERSPROFILE", r"C:\ProgramData")
            return Path(all_users) / "antigravity"
        else:
            return Path("/usr/local/share/antigravity")

    @classmethod
    def deploy_platform_files(
        cls,
        platform_name: str,
        dest_root: Path,
        actions: List[str],
        dry_run: bool = False
    ) -> None:
        """Copies platform-specific adapter files from platforms/<name> into dest_root."""
        # Normalize alias
        lookup_name = "gemini" if platform_name == "antigravity" else platform_name
        plat_dir = SOURCE_PLATFORMS_DIR / lookup_name
        if not plat_dir.exists():
            return

        for item in plat_dir.iterdir():
            target = dest_root / item.name
            actions.append(f"Deploy {lookup_name} adapter [{item.name}] -> {target}")
            if not dry_run:
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)

    @classmethod
    def install(
        cls,
        target_level: str = "project",
        custom_path: Optional[str] = None,
        platform: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Installs the agent package to the specified level and platform.

        Args:
            target_level: 'project' (-p), 'user' (-u), or 'global' (-g).
            custom_path: Optional override directory.
            platform: Platform name ('gemini', 'antigravity', 'claude', 'cursor', 'copilot', 'codex', 'all').
            dry_run: If True, simulates without copying files.
        """
        if custom_path:
            dest_root = Path(custom_path).resolve()
        elif target_level in ("project", "p"):
            dest_root = Path.cwd().resolve()
        elif target_level in ("user", "u"):
            dest_root = cls.get_user_dir()
        elif target_level in ("global", "g"):
            dest_root = cls.get_global_dir()
        else:
            raise ValueError(f"Unknown target level: {target_level}. Must be 'project' (-p), 'user' (-u), or 'global' (-g).")

        plat_key = (platform or "gemini").strip().lower()
        if plat_key not in cls.SUPPORTED_PLATFORMS:
            raise ValueError(
                f"Unknown platform: '{platform}'. Supported platforms: {', '.join(cls.SUPPORTED_PLATFORMS)}"
            )

        dest_agent = dest_root / ".agent"
        dest_env_example = dest_root / ".env.example"
        dest_rules = (dest_root / "rules") if target_level in ("user", "u", "global", "g") else (dest_root / "global-rules")

        actions: List[str] = [
            f"Deploy common .agent/ directory -> {dest_agent}",
            f"Deploy .env.example -> {dest_env_example}",
        ]

        # Determine platforms to deploy
        if plat_key == "all":
            platforms_to_deploy = ["gemini", "claude", "cursor", "copilot", "codex"]
        else:
            platforms_to_deploy = [plat_key]

        for p in platforms_to_deploy:
            cls.deploy_platform_files(p, dest_root, actions, dry_run=dry_run)

        # Global rules for user/global installs
        if plat_key in ("gemini", "antigravity", "all") and SOURCE_GLOBAL_RULES.exists():
            actions.append(f"Deploy global rules -> {dest_rules}")

        if not dry_run:
            dest_root.mkdir(parents=True, exist_ok=True)

            # Copy common .agent directory
            if SOURCE_AGENT_DIR.exists():
                dest_agent.mkdir(parents=True, exist_ok=True)
                subdirs = ["agents", "skills", "workflows", "rules", "context", "memory", "scripts", "resources"]
                for sub in subdirs:
                    src_sub = SOURCE_AGENT_DIR / sub
                    dst_sub = dest_agent / sub
                    if src_sub.exists():
                        shutil.copytree(src_sub, dst_sub, dirs_exist_ok=True)

                # Copy configuration files
                for f in ["mcp.json", "mcp_config.json", ".env.template", "ARCHITECTURE.md"]:
                    src_f = SOURCE_AGENT_DIR / f
                    if src_f.exists():
                        shutil.copy2(src_f, dest_agent / f)

            # Copy .env.example if missing
            if SOURCE_ENV_EXAMPLE.exists() and not (dest_root / ".env").exists():
                shutil.copy2(SOURCE_ENV_EXAMPLE, dest_env_example)

            # Copy global rules if applicable
            if plat_key in ("gemini", "antigravity", "all") and SOURCE_GLOBAL_RULES.exists():
                dest_rules.mkdir(parents=True, exist_ok=True)
                shutil.copytree(SOURCE_GLOBAL_RULES, dest_rules, dirs_exist_ok=True)

        return {
            "target_level": target_level,
            "platform": plat_key,
            "destination": str(dest_root),
            "dry_run": dry_run,
            "actions": actions,
            "status": "SIMULATED" if dry_run else "SUCCESS",
        }


