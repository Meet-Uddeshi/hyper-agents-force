#!/usr/bin/env python3
"""
Meet AI Agents - Unified Command Line Interface.

Usage:
  meet -p                       # Deploy to current project (./.agent/ & GEMINI.md)
  meet -u                       # Deploy to user profile (~/.gemini/)
  meet -g                       # Deploy to system global level
  meet --cursor                 # Deploy for Cursor IDE (.cursorrules & .cursor/rules/)
  meet --claude                 # Deploy for Claude Code (CLAUDE.md & .mcp.json)
  meet --copilot                # Deploy for GitHub Copilot (.github/copilot-instructions.md)
  meet --codex                  # Deploy for OpenAI Codex (.codex/instructions.md)
  meet --all                    # Deploy adapters for all platforms
  meet install [--cursor|--claude|--copilot|--codex|--gemini|--all]
  meet mcp list                 # List configured MCP servers & credential readiness
  meet mcp test <server>        # Test MCP server configuration & tools
  meet mcp sync [-p|-u|-g]      # Sync MCP config to target level
  meet run <workflow>           # Execute workflow automation
  meet answer "<query>"         # Generate structured workflow answer
  meet list [workflows|agents]  # List catalog entries
  meet team board --id <team>   # Display shared team task board & synchronize
  meet hitl list                # Checkpoints awaiting human verification
  meet doctor                   # Health check of workspace, agents & MCP
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = SCRIPT_DIR.parent
AGENT_DIR = WORKSPACE_DIR / ".agent"
SCRIPTS_DIR = AGENT_DIR / "scripts"

sys.path.insert(0, str(WORKSPACE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from bin.installer import Installer
    from bin.mcp_manager import McpManager
    from bin.memory_manager import MemoryManager
    from bin.team_engine import TeamEngine
    from bin.hitl_middleware import HitlMiddleware
except ImportError:
    from installer import Installer
    from mcp_manager import McpManager
    from memory_manager import MemoryManager
    from team_engine import TeamEngine
    from hitl_middleware import HitlMiddleware

# Import workflow engine if available
try:
    from workflow_engine import WorkflowEngine
except ImportError:
    WorkflowEngine = None


def format_header():
    print("================================================================================")
    print("            MEET AI AGENTS - MULTI-AGENT & MCP AUTOMATION PLATFORM              ")
    print("================================================================================")


def handle_install(level: str, custom_path=None, platform=None, dry_run=False, json_output=False):
    res = Installer.install(target_level=level, custom_path=custom_path, platform=platform, dry_run=dry_run)
    if json_output:
        print(json.dumps(res, indent=2))
    else:
        mode_str = "[DRY-RUN] " if dry_run else ""
        plat_str = f" for [{res['platform'].upper()}]" if res.get('platform') else ""
        print(f"\n{mode_str}Successfully deployed Meet AI Agents{plat_str} to [{level.upper()}] level.")
        print(f"Destination: {res['destination']}")
        print("Actions taken:")
        for action in res["actions"]:
            print(f"  - {action}")
        print()


def extract_platform(args) -> Optional[str]:
    if getattr(args, "cursor", False):
        return "cursor"
    if getattr(args, "claude", False):
        return "claude"
    if getattr(args, "copilot", False):
        return "copilot"
    if getattr(args, "codex", False):
        return "codex"
    if getattr(args, "gemini", False):
        return "gemini"
    if getattr(args, "antigravity", False):
        return "antigravity"
    if getattr(args, "all", False):
        return "all"
    if getattr(args, "platform", None):
        return args.platform.lower()
    return None


def handle_mcp(args):
    manager = McpManager()
    subcmd = args.mcp_command

    if subcmd == "list":
        servers = manager.list_servers()
        if args.json:
            print(json.dumps(servers, indent=2))
        else:
            print(f"\nConfigured MCP Servers ({len(servers)}):\n")
            for s in servers:
                status_display = "[READY]" if s["status"] == "READY" else f"[MISSING: {', '.join(s['missing_env'])}]"
                agents_display = ", ".join(s["associated_agents"][:2])
                print(f"- {s['name']:<14} | Status: {status_display:<26} | Agents: {agents_display}")
                print(f"  Command: {s['command']} | Desc: {s['description']}")
            print()

    elif subcmd == "test":
        target = args.server
        try:
            res = manager.test_server(target)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(f"\nMCP Server Diagnostics: {target}")
                print(f"- Status: {'[READY]' if res['ready'] else '[NOT READY]'}")
                print(f"- Command: {res['command']} (Found at: {res['command_path']})")
                if res["missing_env"]:
                    print(f"- Missing Environment Variables: {', '.join(res['missing_env'])}")
                    print(f"  Please add them to your .env file (see .env.example)")
                else:
                    print("- Environment Credentials: All verified.")
                print(f"- Associated Agents: {', '.join(res['associated_agents'])}\n")
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(1)

    elif subcmd == "sync":
        level = args.level or "project"
        if level in ("p", "project"):
            dest = Path.cwd() / ".agent" / "mcp.json"
        elif level in ("u", "user"):
            dest = Installer.get_user_dir() / "antigravity" / "mcp_config.json"
        else:
            dest = Installer.get_global_dir() / "mcp_config.json"

        manager.sync_to_destination(dest)
        print(f"\nSynced MCP configuration to {dest}\n")

    else:
        print("Usage: meet mcp [list|test <server>|sync [-p|-u|-g]]")


def handle_memory(args):
    manager = MemoryManager()
    subcmd = args.memory_command

    if subcmd == "init":
        print(f"\nInitialized SQLite Memory Database: {manager.db_path}\n")

    elif subcmd == "log":
        tags_list = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        meta = json.loads(args.metadata) if args.metadata else {}
        row_id = manager.log_memory(
            key=args.key,
            content=args.content,
            category=args.category,
            agent=args.agent,
            tags=tags_list,
            metadata=meta,
        )
        if args.json:
            print(json.dumps({"success": True, "id": row_id, "key": args.key}))
        else:
            print(f"\nStored memory: key='{args.key}' [Category: {args.category}, Agent: {args.agent}]\n")

    elif subcmd == "query":
        results = manager.query_memories(
            search_term=args.term,
            category=args.category,
            agent=args.agent,
            tag=args.tag,
            limit=args.limit,
        )
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            term_str = f" for '{args.term}'" if args.term else ""
            print(f"\nBounded Memory Query Results{term_str} (Limit: {args.limit}, Found: {len(results)}):\n")
            for idx, r in enumerate(results, start=1):
                cat = r.get("category", "general")
                agt = r.get("agent", "system")
                print(f"{idx}. Key: {r['key']} [Category: {cat}, Agent: {agt}]")
                content_preview = r['content'].strip().replace("\n", " ")
                if len(content_preview) > 120:
                    content_preview = content_preview[:117] + "..."
                print(f"   {content_preview}\n")

    elif subcmd == "sync":
        direction = args.direction or "both"
        imported = {}
        if direction in ("import", "both"):
            imported = manager.sync_from_markdown()
        if direction in ("export", "both"):
            manager.sync_to_markdown()

        if args.json:
            print(json.dumps({"direction": direction, "imported": imported}))
        else:
            print(f"\nDual-Mode Memory Synchronization Completed (Direction: {direction}):")
            if imported:
                print(f"- Synced Invariants from ARCHITECTURE_MEMORY.md: {imported.get('synced_invariants', 0)}")
                print(f"- Synced Events from BLACKBOARD.md: {imported.get('synced_events', 0)}")
            print("- Synchronized markdown files with SQLite storage.\n")

    elif subcmd == "stats":
        stats = manager.get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\nSQLite Memory & Context Engineering Stats:")
            print(f"- Database Path: {stats['db_path']}")
            print(f"- Database Size: {stats['size_kb']} KB ({stats['size_bytes']} bytes)")
            print(f"- Total Memories: {stats['total_memories']}")
            print(f"- Total Blackboard Events: {stats['total_events']}")
            print(f"- Total Active Teams: {stats.get('total_teams', 0)}")
            print(f"- Total Team Tasks: {stats.get('total_team_tasks', 0)}")
            print(f"- Total Team Messages: {stats.get('total_team_messages', 0)}")
            print(f"- Total HITL Checkpoints: {stats.get('total_hitl', 0)} (Pending: {stats.get('pending_hitl', 0)})")
            print("- Categories Breakdown:")
            for cat, count in stats.get("categories", {}).items():
                print(f"  * {cat}: {count}")
            print()

    elif subcmd == "prune":
        count = manager.prune(max_age_days=args.days, keep_invariants=not args.all)
        if args.json:
            print(json.dumps({"pruned_records": count, "max_age_days": args.days}))
        else:
            print(f"\nPruned {count} historical records older than {args.days} days.\n")

    elif subcmd == "events":
        events = manager.query_events(
            session_id=args.session,
            agent=args.agent,
            event_type=args.type,
            limit=args.limit,
        )
        if args.json:
            print(json.dumps(events, indent=2, default=str))
        else:
            print(f"\nRecent Blackboard & Coordination Events (Limit: {args.limit}, Found: {len(events)}):\n")
            for idx, e in enumerate(events, start=1):
                print(f"{idx}. [{e['created_at']}] [{e['agent']}] ({e['event_type']})")
                print(f"   {e['description']}\n")
    else:
        print("Usage: meet memory [init|log|query|sync|stats|prune|events]")


def handle_team(args):
    engine = TeamEngine()
    subcmd = args.team_command

    if subcmd == "create":
        members = []
        if args.members:
            try:
                parsed = json.loads(args.members)
                if isinstance(parsed, list):
                    for m in parsed:
                        if isinstance(m, str):
                            members.append({"agent_name": m, "role_description": "Team Specialist", "skills": []})
                        elif isinstance(m, dict):
                            members.append(m)
            except Exception:
                for name in args.members.split(","):
                    name = name.strip()
                    if name:
                        members.append({"agent_name": name, "role_description": "Team Specialist", "skills": []})

        tid = engine.create_team(
            team_id=args.id,
            team_name=args.name,
            lead_agent=args.lead,
            objective=args.objective,
            members=members
        )
        board = engine.get_board_data(tid)
        if args.json:
            print(json.dumps(board, indent=2))
        else:
            team_meta = board.get("team") or {}
            print(f"\nCreated Collaborative Agent Team: {team_meta.get('team_name', args.name)} [{tid}]")
            print(f"- Lead Agent: {team_meta.get('lead_agent', args.lead)}")
            print(f"- Objective: {team_meta.get('objective', args.objective)}")
            print(f"- Members: {len(board.get('members', []))}\n")

    elif subcmd == "task-add":
        deps = [d.strip() for d in args.deps.split(",") if d.strip()] if args.deps else []
        task = engine.add_task(
            team_id=args.id,
            title=args.title,
            description=args.desc,
            depends_on=deps,
            task_id=args.task_id
        )
        if args.json:
            print(json.dumps(task, indent=2))
        else:
            print(f"\nAdded Task to Team '{args.id}': [{task['task_id']}] {task['title']}")
            print(f"- Status: {task['status']}")
            print(f"- Dependencies: {task['depends_on']}\n")

    elif subcmd == "tasks":
        if args.unblocked:
            tasks = engine.get_unblocked_tasks(args.id)
            title_prefix = "Unblocked / Ready"
        else:
            board = engine.get_board_data(args.id)
            tasks = board.get("tasks", [])
            title_prefix = "All"

        if args.json:
            print(json.dumps(tasks, indent=2))
        else:
            print(f"\nTeam '{args.id}' {title_prefix} Tasks ({len(tasks)}):\n")
            for t in tasks:
                claimed = f" [Claimed: {t['claimed_by']}]" if t.get("claimed_by") else ""
                print(f"- [{t['task_id']}] ({t['status']}){claimed} {t['title']}")
                print(f"  Description: {t['description']}")
            print()

    elif subcmd == "claim":
        success = engine.claim_task(team_id=args.id, task_id=args.task_id, agent_name=args.agent)
        if args.json:
            print(json.dumps({"success": success, "team_id": args.id, "task_id": args.task_id, "agent": args.agent}))
        else:
            if success:
                print(f"\nTask [{args.task_id}] successfully claimed by agent @{args.agent} in team '{args.id}'.\n")
            else:
                print(f"\nFailed to claim task [{args.task_id}]. It may be blocked or already claimed.\n", file=sys.stderr)
                sys.exit(1)

    elif subcmd == "complete":
        outs = [o.strip() for o in args.outputs.split(",") if o.strip()] if args.outputs else []
        success = engine.complete_task(team_id=args.id, task_id=args.task_id, agent_name=args.agent, output_artifacts=outs)
        if args.json:
            print(json.dumps({"success": success, "team_id": args.id, "task_id": args.task_id, "agent": args.agent}))
        else:
            if success:
                print(f"\nTask [{args.task_id}] completed by agent @{args.agent}. Dependent tasks unblocked.\n")
            else:
                print(f"\nFailed to complete task [{args.task_id}]. Verify agent ownership and task status.\n", file=sys.stderr)
                sys.exit(1)

    elif subcmd == "msg":
        msg_id = engine.send_message(
            team_id=args.id,
            from_agent=args.from_agent,
            to_agent=args.to_agent,
            content=args.content,
            reply_to=args.reply_to
        )
        if args.json:
            print(json.dumps({"success": True, "message_id": msg_id}))
        else:
            print(f"\nMessage #{msg_id} delivered from @{args.from_agent} to @{args.to_agent} in team '{args.id}'.\n")

    elif subcmd == "board":
        if args.sync:
            synced_file = engine.sync_markdown_board(args.id)
            if not args.json:
                print(f"Synchronized Team Board to Markdown: {synced_file}\n")
        if args.json:
            print(json.dumps(engine.get_board_data(args.id), indent=2))
        else:
            print(engine.render_markdown_board(args.id))

    elif subcmd == "route":
        classification = TeamEngine.classify_prompt_intent(args.prompt)
        if args.json:
            print(json.dumps(classification, indent=2))
        else:
            print("\nAutonomous Prompt Intent Classification:")
            print(f"- Selected System: {classification['system'].upper()}")
            print(f"- Detection Mode: {classification['mode']}")
            print(f"- Identifier: {classification['identifier']}")
            print(f"- Confidence: {classification['confidence']:.2f}\n")

    elif subcmd == "list":
        teams = engine.list_teams()
        if args.json:
            print(json.dumps(teams, indent=2))
        else:
            print(f"\nRegistered Collaborative Agent Teams ({len(teams)}):\n")
            for t in teams:
                print(f"- [{t['team_id']}] {t['team_name']} (Lead: @{t['lead_agent']}, Status: {t['status']})")
                print(f"  Objective: {t['objective']}\n")
    else:
        print("Usage: meet team [create|list|task-add|tasks|claim|complete|msg|board|route]")


def handle_hitl(args):
    middleware = HitlMiddleware()
    subcmd = args.hitl_command

    if subcmd == "list":
        checkpoints = middleware.list_checkpoints(
            status=args.status,
            stage=args.stage,
            team_id=args.team,
            agent_name=args.agent,
            limit=args.limit
        )
        if args.json:
            print(json.dumps(checkpoints, indent=2, default=str))
        else:
            print(f"\nHuman-in-the-Loop Checkpoints ({len(checkpoints)}):\n")
            if not checkpoints:
                print("  - No checkpoints matching filter.\n")
            for cp in checkpoints:
                st = f"[{cp['status']}]"
                print(f"- {st:<10} ID: {cp['checkpoint_id']} | Stage: {cp['stage']:<20} | Agent: @{cp['agent_name']}")
                print(f"  Summary: {cp['summary']}")
                if cp.get("user_feedback"):
                    print(f"  Feedback: {cp['user_feedback']}")
                print()

    elif subcmd == "show":
        cp = middleware.get_checkpoint(args.checkpoint_id)
        if not cp:
            print(f"[ERROR] Checkpoint '{args.checkpoint_id}' not found.", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(cp, indent=2, default=str))
        else:
            print("\n" + middleware.render_checkpoint_prompt(args.checkpoint_id) + "\n")

    elif subcmd == "approve":
        try:
            res = middleware.resolve_checkpoint(args.checkpoint_id, status="APPROVED", user_feedback=args.feedback)
            if args.json:
                print(json.dumps(res, indent=2, default=str))
            else:
                print(f"\n[APPROVED] Checkpoint [{args.checkpoint_id}] has been approved.")
                if args.feedback:
                    print(f"User Feedback: {args.feedback}")
                print("Agents may now proceed past this gate.\n")
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(1)

    elif subcmd == "reject":
        try:
            res = middleware.resolve_checkpoint(args.checkpoint_id, status="REJECTED", user_feedback=args.feedback)
            if args.json:
                print(json.dumps(res, indent=2, default=str))
            else:
                print(f"\n[REJECTED] Checkpoint [{args.checkpoint_id}] has been rejected / revision requested.")
                if args.feedback:
                    print(f"User Feedback: {args.feedback}")
                print("Agents must rework deliverables or clarify assumptions.\n")
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(1)

    elif subcmd == "request":
        try:
            payload = json.loads(args.context) if args.context else {}
        except Exception:
            payload = {"raw_context": args.context}

        res = middleware.create_checkpoint(
            system_type=args.system,
            stage=args.stage,
            agent_name=args.agent,
            summary=args.summary,
            context_payload=payload,
            team_id=args.team,
            checkpoint_id=args.id
        )
        if args.json:
            print(json.dumps(res, indent=2, default=str))
        else:
            print(f"\nCreated HITL Checkpoint: [{res['checkpoint_id']}]")
            print(f"- Stage:  {res['stage']}")
            print(f"- System: {res['system_type']}")
            print(f"- Agent:  @{res['agent_name']}")
            print(f"- Status: PENDING (Awaiting human verification)\n")
    else:
        print("Usage: meet hitl [list|show|approve|reject|request]")


def handle_run(args):
    if not WorkflowEngine:
        print("[ERROR] WorkflowEngine could not be loaded from .agent/scripts", file=sys.stderr)
        sys.exit(1)
    engine = WorkflowEngine()
    try:
        res = engine.run_workflow(
            workflow_name=args.workflow,
            args=args.args,
            agent_name=args.agent,
            dry_run=args.dry_run
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            mode_str = "[DRY-RUN]" if args.dry_run else "[EXECUTED]"
            print(f"\n{mode_str} Workflow /{res['workflow']} run completed successfully.")
            print(f"- Executing Agent: {res['agent']}")
            print(f"- Steps loaded: {len(res['steps'])}")
            print(f"- Blackboard updated: {'No (dry-run)' if args.dry_run else 'Yes'}\n")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def handle_answer(args):
    if not WorkflowEngine:
        print("[ERROR] WorkflowEngine could not be loaded", file=sys.stderr)
        sys.exit(1)
    
    intent = TeamEngine.classify_prompt_intent(args.query)
    engine = WorkflowEngine()
    ans = engine.generate_answer(query=args.query, explicit_agent=args.agent)
    ans["intent"] = intent

    if args.json:
        print(json.dumps(ans, indent=2))
    else:
        from workflow_engine import format_answer_markdown
        print("\n" + format_answer_markdown(ans) + "\n")


def handle_list(args):
    target = args.target or "workflows"
    if target == "mcp":
        manager = McpManager()
        servers = manager.list_servers()
        print(f"\nMCP Servers ({len(servers)}): " + ", ".join(s["name"] for s in servers) + "\n")
    else:
        if not WorkflowEngine:
            print("[ERROR] WorkflowEngine could not be loaded", file=sys.stderr)
            sys.exit(1)
        engine = WorkflowEngine()
        wf_list = engine.list_workflows()
        print(f"\nAvailable Workflows ({len(wf_list)}):")
        for wf in wf_list:
            print(f"  - /{wf['name']:<18} | {wf['description'][:60]}...")
        print()


def handle_doctor():
    format_header()
    print("Running Meet AI Agents System Health Check...")
    print(f"- Workspace root: {WORKSPACE_DIR}")
    print(f"- .agent bundle: {'[OK]' if AGENT_DIR.exists() else '[FAIL]'}")
    print(f"- GEMINI.md: {'[OK]' if (WORKSPACE_DIR / 'GEMINI.md').exists() else '[FAIL]'}")
    print(f"- .env.example: {'[OK]' if (WORKSPACE_DIR / '.env.example').exists() else '[FAIL]'}")

    manager = McpManager()
    servers = manager.list_servers()
    print(f"- Configured MCP Servers: {len(servers)}")
    for s in servers:
        print(f"  * {s['name']}: {s['status']}")

    try:
        mem_mgr = MemoryManager()
        stats = mem_mgr.get_stats()
        print(f"- SQLite Memory DB: [OK] ({stats['size_kb']} KB, {stats['total_memories']} memories, {stats['total_events']} events, {stats.get('total_teams', 0)} teams)")
    except Exception as e:
        print(f"- SQLite Memory DB: [FAIL] ({e})")

    if WorkflowEngine:
        engine = WorkflowEngine()
        print(f"- Registered Workflows: {len(engine.list_workflows())}")
    print("Health check completed successfully.\n")


def main():
    parser = argparse.ArgumentParser(
        prog="meet",
        description="Meet AI Agents - Multi-Agent System & Automation Platform"
    )

    # Top-level direct deployment flags
    parser.add_argument("-p", "--project", action="store_true", help="Deploy to current project level (./.agent/)")
    parser.add_argument("-u", "--user", action="store_true", help="Deploy to user profile level (~/.gemini/)")
    parser.add_argument("-g", "--global", dest="global_level", action="store_true", help="Deploy to system global level")
    parser.add_argument("--cursor", action="store_true", help="Install adapter for Cursor IDE (.cursorrules, .cursor/)")
    parser.add_argument("--claude", action="store_true", help="Install adapter for Claude Code (CLAUDE.md, .mcp.json)")
    parser.add_argument("--copilot", action="store_true", help="Install adapter for GitHub Copilot (.github/)")
    parser.add_argument("--codex", action="store_true", help="Install adapter for OpenAI Codex (.codex/)")
    parser.add_argument("--gemini", action="store_true", help="Install adapter for Gemini CLI (GEMINI.md)")
    parser.add_argument("--antigravity", action="store_true", help="Install adapter for Antigravity (GEMINI.md)")
    parser.add_argument("--all", action="store_true", help="Install adapters for all supported platforms")
    parser.add_argument("--platform", type=str, default=None, choices=Installer.SUPPORTED_PLATFORMS, help="Specify platform adapter")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deployment without modifying disk")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")

    # Subcommand: install
    install_parser = subparsers.add_parser("install", help="Deploy Meet AI Agents to target level and platform")
    install_parser.add_argument("-p", "--project", action="store_true", help="Target current project")
    install_parser.add_argument("-u", "--user", action="store_true", help="Target user profile (~/.gemini/)")
    install_parser.add_argument("-g", "--global", dest="global_level", action="store_true", help="Target system global")
    install_parser.add_argument("--cursor", action="store_true", help="Install adapter for Cursor IDE (.cursorrules, .cursor/)")
    install_parser.add_argument("--claude", action="store_true", help="Install adapter for Claude Code (CLAUDE.md, .mcp.json)")
    install_parser.add_argument("--copilot", action="store_true", help="Install adapter for GitHub Copilot (.github/)")
    install_parser.add_argument("--codex", action="store_true", help="Install adapter for OpenAI Codex (.codex/)")
    install_parser.add_argument("--gemini", action="store_true", help="Install adapter for Gemini CLI (GEMINI.md)")
    install_parser.add_argument("--antigravity", action="store_true", help="Install adapter for Antigravity (GEMINI.md)")
    install_parser.add_argument("--all", action="store_true", help="Install adapters for all supported platforms")
    install_parser.add_argument("--platform", type=str, default=None, choices=Installer.SUPPORTED_PLATFORMS, help="Specify platform adapter")
    install_parser.add_argument("--path", type=str, default=None, help="Custom target directory")
    install_parser.add_argument("--dry-run", action="store_true", help="Simulate without copying")
    install_parser.add_argument("--json", action="store_true", help="Output in JSON")

    # Subcommand: mcp
    mcp_parser = subparsers.add_parser("mcp", help="Manage MCP servers & 3rd-party integrations")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_command", help="MCP action")
    list_p = mcp_sub.add_parser("list", help="List configured MCP servers")
    list_p.add_argument("--json", action="store_true", help="Output in JSON")
    test_p = mcp_sub.add_parser("test", help="Test specific MCP server")
    test_p.add_argument("server", type=str, help="MCP server name (e.g. github, jira)")
    test_p.add_argument("--json", action="store_true", help="Output in JSON")
    sync_p = mcp_sub.add_parser("sync", help="Sync MCP config to destination")
    sync_p.add_argument("-l", "--level", choices=["project", "user", "global"], default="project", help="Destination level")

    # Subcommand: run
    run_parser = subparsers.add_parser("run", help="Run workflow automation")
    run_parser.add_argument("workflow", type=str, help="Workflow name (e.g. mobile-test, audit, deploy)")
    run_parser.add_argument("--args", type=str, default="", help="Workflow arguments")
    run_parser.add_argument("--agent", type=str, default=None, help="Agent override")
    run_parser.add_argument("--dry-run", action="store_true", help="Simulate run without blackboard log")
    run_parser.add_argument("--json", action="store_true", help="Output in JSON")

    # Subcommand: answer
    answer_parser = subparsers.add_parser("answer", help="Generate structured workflow answer")
    answer_parser.add_argument("query", type=str, help="User prompt or query")
    answer_parser.add_argument("--agent", type=str, default=None, help="Agent override")
    answer_parser.add_argument("--json", action="store_true", help="Output in JSON")

    # Subcommand: list
    list_parser = subparsers.add_parser("list", help="List workflows or MCP servers")
    list_parser.add_argument("target", nargs="?", choices=["workflows", "mcp"], default="workflows")

    # Subcommand: memory
    mem_parser = subparsers.add_parser("memory", help="SQLite persistent memory, bounded query & context engineering")
    mem_sub = mem_parser.add_subparsers(dest="memory_command", help="Memory action")
    
    mem_init = mem_sub.add_parser("init", help="Initialize SQLite memory database")
    mem_init.add_argument("--json", action="store_true", help="Output in JSON")
    
    mem_log = mem_sub.add_parser("log", help="Store or update indexed memory")
    mem_log.add_argument("--key", type=str, required=True, help="Unique memory key (e.g. invariant:name, note:topic)")
    mem_log.add_argument("--content", type=str, required=True, help="Memory content / invariant rule")
    mem_log.add_argument("--category", type=str, default="general", help="Category (invariant, architecture, decision, failure)")
    mem_log.add_argument("--agent", type=str, default="system", help="Author agent name")
    mem_log.add_argument("--tags", type=str, default="", help="Comma-separated tags")
    mem_log.add_argument("--metadata", type=str, default="{}", help="JSON metadata string")
    mem_log.add_argument("--json", action="store_true", help="Output in JSON")

    mem_query = mem_sub.add_parser("query", help="Bounded memory query & FTS5 search")
    mem_query.add_argument("term", nargs="?", type=str, default=None, help="Search query string")
    mem_query.add_argument("--category", type=str, default=None, help="Filter by category")
    mem_query.add_argument("--agent", type=str, default=None, help="Filter by agent")
    mem_query.add_argument("--tag", type=str, default=None, help="Filter by tag substring")
    mem_query.add_argument("--limit", type=int, default=5, help="Maximum records to return (default: 5)")
    mem_query.add_argument("--json", action="store_true", help="Output in JSON")

    mem_sync = mem_sub.add_parser("sync", help="Dual-mode sync between SQLite and Markdown files")
    mem_sync.add_argument("-d", "--direction", choices=["import", "export", "both"], default="both", help="Sync direction")
    mem_sync.add_argument("--json", action="store_true", help="Output in JSON")

    mem_stats = mem_sub.add_parser("stats", help="Show SQLite database size, counts, and category statistics")
    mem_stats.add_argument("--json", action="store_true", help="Output in JSON")

    mem_prune = mem_sub.add_parser("prune", help="Prune older historical records")
    mem_prune.add_argument("--days", type=int, default=30, help="Days threshold (default: 30)")
    mem_prune.add_argument("--all", action="store_true", help="Also prune non-invariant memories")
    mem_prune.add_argument("--json", action="store_true", help="Output in JSON")

    mem_ev = mem_sub.add_parser("events", help="List recent blackboard and coordination events")
    mem_ev.add_argument("--session", type=str, default=None, help="Filter by session ID")
    mem_ev.add_argument("--agent", type=str, default=None, help="Filter by agent")
    mem_ev.add_argument("--type", type=str, default=None, help="Filter by event type")
    mem_ev.add_argument("--limit", type=int, default=10, help="Maximum events to return (default: 10)")
    mem_ev.add_argument("--json", action="store_true", help="Output in JSON")

    # Subcommand: team
    team_parser = subparsers.add_parser("team", help="Collaborative Agent Team management, task claiming & peer communication")
    team_sub = team_parser.add_subparsers(dest="team_command", help="Team action")

    team_create = team_sub.add_parser("create", help="Create new collaborative agent team")
    team_create.add_argument("--id", type=str, required=True, help="Unique team identifier (e.g. team-fullstack)")
    team_create.add_argument("--name", type=str, required=True, help="Human-readable team name")
    team_create.add_argument("--lead", type=str, required=True, help="Lead agent name (e.g. orchestrator, architect)")
    team_create.add_argument("--objective", type=str, required=True, help="High-level team goal or mission")
    team_create.add_argument("--members", type=str, default="", help="JSON list or comma-separated agent names")
    team_create.add_argument("--json", action="store_true", help="Output in JSON")

    team_list = team_sub.add_parser("list", help="List all registered collaborative teams in SQLite")
    team_list.add_argument("--json", action="store_true", help="Output in JSON")

    team_task = team_sub.add_parser("task-add", help="Add task to team shared board")
    team_task.add_argument("--id", type=str, required=True, help="Team ID")
    team_task.add_argument("--title", type=str, required=True, help="Task title")
    team_task.add_argument("--desc", type=str, required=True, help="Detailed task requirements")
    team_task.add_argument("--deps", type=str, default="", help="Comma-separated dependent task IDs")
    team_task.add_argument("--task-id", type=str, default=None, help="Explicit task ID (e.g. task-001)")
    team_task.add_argument("--json", action="store_true", help="Output in JSON")

    team_tasks = team_sub.add_parser("tasks", help="List team tasks")
    team_tasks.add_argument("--id", type=str, required=True, help="Team ID")
    team_tasks.add_argument("--unblocked", action="store_true", help="Show only unblocked tasks ready to claim")
    team_tasks.add_argument("--json", action="store_true", help="Output in JSON")

    team_claim = team_sub.add_parser("claim", help="Claim an unblocked task for an agent")
    team_claim.add_argument("--id", type=str, required=True, help="Team ID")
    team_claim.add_argument("--task-id", type=str, required=True, help="Task ID to claim")
    team_claim.add_argument("--agent", type=str, required=True, help="Claiming agent name")
    team_claim.add_argument("--json", action="store_true", help="Output in JSON")

    team_comp = team_sub.add_parser("complete", help="Complete a claimed task and unblock dependents")
    team_comp.add_argument("--id", type=str, required=True, help="Team ID")
    team_comp.add_argument("--task-id", type=str, required=True, help="Task ID to mark complete")
    team_comp.add_argument("--agent", type=str, required=True, help="Completing agent name")
    team_comp.add_argument("--outputs", type=str, default="", help="Comma-separated output artifacts / file paths")
    team_comp.add_argument("--json", action="store_true", help="Output in JSON")

    team_msg = team_sub.add_parser("msg", help="Send peer message between teammates")
    team_msg.add_argument("--id", type=str, required=True, help="Team ID")
    team_msg.add_argument("--from-agent", type=str, required=True, help="Sender agent name")
    team_msg.add_argument("--to-agent", type=str, default="ALL", help="Target agent name or 'ALL'")
    team_msg.add_argument("--content", type=str, required=True, help="Message body or review feedback")
    team_msg.add_argument("--reply-to", type=int, default=None, help="Optional parent message ID")
    team_msg.add_argument("--json", action="store_true", help="Output in JSON")

    team_board = team_sub.add_parser("board", help="Display or synchronize team task board")
    team_board.add_argument("--id", type=str, required=True, help="Team ID")
    team_board.add_argument("--sync", action="store_true", default=True, help="Synchronize to .agent/context/TEAM_BOARD.md")
    team_board.add_argument("--no-sync", dest="sync", action="store_false", help="Skip Markdown sync")
    team_board.add_argument("--json", action="store_true", help="Output in JSON")

    team_route = team_sub.add_parser("route", help="Classify prompt intent (Subagent vs Agent Team)")
    team_route.add_argument("prompt", type=str, help="Prompt text to classify")
    team_route.add_argument("--json", action="store_true", help="Output in JSON")

    # Subcommand: hitl
    hitl_parser = subparsers.add_parser("hitl", help="Human-in-the-Loop (HITL) middleware checkpoints, alignment & sign-offs")
    hitl_sub = hitl_parser.add_subparsers(dest="hitl_command", help="HITL action")

    hitl_list = hitl_sub.add_parser("list", help="List checkpoints awaiting human verification")
    hitl_list.add_argument("--status", choices=["PENDING", "APPROVED", "REJECTED", "CLARIFIED"], default=None, help="Filter by status")
    hitl_list.add_argument("--stage", choices=["DOMAIN_KNOWLEDGE", "PLAN_APPROVAL", "VERIFICATION_SIGNOFF"], default=None, help="Filter by stage")
    hitl_list.add_argument("--team", type=str, default=None, help="Filter by team ID")
    hitl_list.add_argument("--agent", type=str, default=None, help="Filter by agent name")
    hitl_list.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    hitl_list.add_argument("--json", action="store_true", help="Output in JSON")

    hitl_show = hitl_sub.add_parser("show", help="Display structured checkpoint verification card")
    hitl_show.add_argument("checkpoint_id", type=str, help="Checkpoint ID (e.g. hitl-domain-...)")
    hitl_show.add_argument("--json", action="store_true", help="Output in JSON")

    hitl_app = hitl_sub.add_parser("approve", help="Approve checkpoint and permit execution to proceed")
    hitl_app.add_argument("checkpoint_id", type=str, help="Checkpoint ID to approve")
    hitl_app.add_argument("--feedback", type=str, default="Approved", help="Optional human verification feedback")
    hitl_app.add_argument("--json", action="store_true", help="Output in JSON")

    hitl_rej = hitl_sub.add_parser("reject", help="Reject checkpoint or request changes")
    hitl_rej.add_argument("checkpoint_id", type=str, help="Checkpoint ID to reject")
    hitl_rej.add_argument("--feedback", type=str, required=True, help="Reason for rejection or requested changes")
    hitl_rej.add_argument("--json", action="store_true", help="Output in JSON")

    hitl_req = hitl_sub.add_parser("request", help="Create new HITL checkpoint")
    hitl_req.add_argument("--system", choices=["subagent", "team"], default="subagent", help="System architecture")
    hitl_req.add_argument("--stage", choices=["DOMAIN_KNOWLEDGE", "PLAN_APPROVAL", "VERIFICATION_SIGNOFF"], required=True, help="Checkpoint gate stage")
    hitl_req.add_argument("--agent", type=str, required=True, help="Agent creating checkpoint")
    hitl_req.add_argument("--summary", type=str, required=True, help="Summary of decision, plan, or evidence")
    hitl_req.add_argument("--team", type=str, default=None, help="Optional Team ID")
    hitl_req.add_argument("--context", type=str, default="{}", help="JSON context payload")
    hitl_req.add_argument("--id", type=str, default=None, help="Optional explicit checkpoint ID")
    hitl_req.add_argument("--json", action="store_true", help="Output in JSON")

    # Subcommand: doctor
    subparsers.add_parser("doctor", help="Run system diagnostics")

    args = parser.parse_args()

    # Determine requested platform (if any)
    platform = extract_platform(args)

    # Handle direct flags (-p, -u, -g) or platform flags invoked directly
    if args.project or (platform is not None and args.subcommand is None):
        target = "user" if args.user else ("global" if args.global_level else "project")
        handle_install(target, platform=platform, dry_run=args.dry_run, json_output=args.json)
        return
    elif args.user:
        handle_install("user", platform=platform, dry_run=args.dry_run, json_output=args.json)
        return
    elif args.global_level:
        handle_install("global", platform=platform, dry_run=args.dry_run, json_output=args.json)
        return

    # Handle subcommands
    if args.subcommand == "install":
        level = "project"
        if args.user:
            level = "user"
        elif args.global_level:
            level = "global"
        handle_install(level, custom_path=args.path, platform=platform, dry_run=args.dry_run, json_output=args.json)
    elif args.subcommand == "mcp":
        handle_mcp(args)
    elif args.subcommand == "run":
        handle_run(args)
    elif args.subcommand == "answer":
        handle_answer(args)
    elif args.subcommand == "list":
        handle_list(args)
    elif args.subcommand == "memory":
        handle_memory(args)
    elif args.subcommand == "team":
        handle_team(args)
    elif args.subcommand == "hitl":
        handle_hitl(args)
    elif args.subcommand == "doctor":
        handle_doctor()
    else:
        format_header()
        parser.print_help()


if __name__ == "__main__":
    main()

