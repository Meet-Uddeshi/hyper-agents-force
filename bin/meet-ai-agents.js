#!/usr/bin/env node
/**
 * Meet AI Agents - Unified Node.js CLI & Package Runner.
 *
 * Usage:
 *   npx meet-ai-agents -p       # Deploy to current project (./.agent/ & GEMINI.md)
 *   npx meet-ai-agents -u       # Deploy to user profile (~/.gemini/)
 *   npx meet-ai-agents -g       # Deploy to system global level
 *   npx meet-ai-agents mcp list # Check MCP 3rd-party integrations
 *   npx meet-ai-agents run <wf> # Execute workflow automation
 *   npx meet-ai-agents answer   # Formulate structured workflow answer
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

const WORKSPACE_DIR = path.resolve(__dirname, '..');
const SOURCE_AGENT_DIR = path.join(WORKSPACE_DIR, '.agent');
const SOURCE_GEMINI_MD = path.join(WORKSPACE_DIR, 'GEMINI.md');
const SOURCE_ENV_EXAMPLE = path.join(WORKSPACE_DIR, '.env.example');
const SOURCE_GLOBAL_RULES = path.join(WORKSPACE_DIR, 'global-rules');
const SOURCE_PLATFORMS_DIR = path.join(WORKSPACE_DIR, 'platforms');
const MCP_JSON_PATH = path.join(SOURCE_AGENT_DIR, 'mcp.json');

const SUPPORTED_PLATFORMS = ['gemini', 'antigravity', 'claude', 'cursor', 'copilot', 'codex', 'all'];

function copyRecursive(src, dst) {
  if (!fs.existsSync(src)) return;
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (!fs.existsSync(dst)) fs.mkdirSync(dst, { recursive: true });
    for (const file of fs.readdirSync(src)) {
      copyRecursive(path.join(src, file), path.join(dst, file));
    }
  } else {
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.copyFileSync(src, dst);
  }
}

function getUserDir() {
  return path.join(os.homedir(), '.gemini');
}

function getGlobalDir() {
  if (os.platform() === 'win32') {
    const programData = process.env.ALLUSERSPROFILE || 'C:\\ProgramData';
    return path.join(programData, 'antigravity');
  }
  return '/usr/local/share/antigravity';
}

function getPlatform(args) {
  if (args.includes('--cursor')) return 'cursor';
  if (args.includes('--claude')) return 'claude';
  if (args.includes('--copilot')) return 'copilot';
  if (args.includes('--codex')) return 'codex';
  if (args.includes('--gemini')) return 'gemini';
  if (args.includes('--antigravity')) return 'antigravity';
  if (args.includes('--all')) return 'all';
  const platIdx = args.indexOf('--platform');
  if (platIdx !== -1 && args[platIdx + 1]) {
    return args[platIdx + 1].toLowerCase();
  }
  return null;
}

function deployPlatformFiles(platformName, destRoot, dryRun = false) {
  const lookupName = platformName === 'antigravity' ? 'gemini' : platformName;
  const platDir = path.join(SOURCE_PLATFORMS_DIR, lookupName);
  if (!fs.existsSync(platDir)) return;

  for (const item of fs.readdirSync(platDir)) {
    const srcItem = path.join(platDir, item);
    const dstItem = path.join(destRoot, item);
    console.log(`  - Deploy ${lookupName} adapter [${item}] -> ${dstItem}`);
    if (!dryRun) {
      copyRecursive(srcItem, dstItem);
    }
  }
}

function handleInstall(level, customPath = null, dryRun = false, platform = null) {
  let destRoot;
  if (customPath) {
    destRoot = path.resolve(customPath);
  } else if (level === 'project' || level === 'p') {
    destRoot = process.cwd();
  } else if (level === 'user' || level === 'u') {
    destRoot = getUserDir();
  } else if (level === 'global' || level === 'g') {
    destRoot = getGlobalDir();
  } else {
    console.error(`[ERROR] Unknown target level: ${level}. Use -p, -u, or -g.`);
    process.exit(1);
  }

  const platKey = (platform || 'gemini').toLowerCase();
  if (!SUPPORTED_PLATFORMS.includes(platKey)) {
    console.error(`[ERROR] Unsupported platform: '${platform}'. Supported: ${SUPPORTED_PLATFORMS.join(', ')}`);
    process.exit(1);
  }

  const destAgent = path.join(destRoot, '.agent');
  const destEnvExample = path.join(destRoot, '.env.example');
  const destRules = (level === 'user' || level === 'u' || level === 'global' || level === 'g')
    ? path.join(destRoot, 'rules')
    : path.join(destRoot, 'global-rules');

  const platDisplay = platform ? ` for [${platKey.toUpperCase()}]` : '';
  console.log(`\n${dryRun ? '[DRY-RUN] ' : ''}Deploying Hyper Agents Force${platDisplay} to [${level.toUpperCase()}] level...`);
  console.log(`Target Destination: ${destRoot}`);

  if (!dryRun) {
    if (fs.existsSync(SOURCE_AGENT_DIR)) {
      copyRecursive(SOURCE_AGENT_DIR, destAgent);
      console.log(`  - Deployed common .agent/ bundle -> ${destAgent}`);
    }
    if (fs.existsSync(SOURCE_ENV_EXAMPLE) && !fs.existsSync(path.join(destRoot, '.env'))) {
      fs.copyFileSync(SOURCE_ENV_EXAMPLE, destEnvExample);
      console.log(`  - Deployed .env.example -> ${destEnvExample}`);
    }
  } else {
    console.log(`  - Deploy common .agent/ bundle -> ${destAgent}`);
    console.log(`  - Deploy .env.example -> ${destEnvExample}`);
  }

  // Deploy platform adapters
  const platformsToDeploy = platKey === 'all'
    ? ['gemini', 'claude', 'cursor', 'copilot', 'codex']
    : [platKey];

  for (const p of platformsToDeploy) {
    deployPlatformFiles(p, destRoot, dryRun);
  }

  if (['gemini', 'antigravity', 'all'].includes(platKey) && fs.existsSync(SOURCE_GLOBAL_RULES)) {
    console.log(`  - Deploy global rules -> ${destRules}`);
    if (!dryRun) {
      copyRecursive(SOURCE_GLOBAL_RULES, destRules);
    }
  }

  console.log('Deployment completed successfully.\n');
}

function handleMcpList() {
  if (!fs.existsSync(MCP_JSON_PATH)) {
    console.error('[WARN] mcp.json not found in .agent directory.');
    return;
  }
  const data = JSON.parse(fs.readFileSync(MCP_JSON_PATH, 'utf-8'));
  const servers = data.mcpServers || {};
  console.log(`\nConfigured MCP Servers (${Object.keys(servers).length}):\n`);
  for (const [name, cfg] of Object.entries(servers)) {
    const envVars = cfg.env || {};
    const missing = [];
    for (const [k, v] of Object.entries(envVars)) {
      const match = String(v).match(/\$\{([^}]+)\}/);
      if (match && !process.env[match[1]]) {
        missing.push(match[1]);
      }
    }
    const status = missing.length === 0 ? '[READY]' : `[MISSING: ${missing.join(', ')}]`;
    const agents = (cfg.associated_agents || []).slice(0, 2).join(', ');
    console.log(`- ${name.padEnd(14)} | Status: ${status.padEnd(26)} | Agents: ${agents}`);
    console.log(`  Command: ${cfg.command} | Desc: ${cfg.description}`);
  }
  console.log();
}

function handleDoctor() {
  console.log('================================================================================');
  console.log('            MEET AI AGENTS - SYSTEM HEALTH CHECK (NODE.JS)                      ');
  console.log('================================================================================');
  console.log(`- Workspace root: ${WORKSPACE_DIR}`);
  console.log(`- .agent directory: ${fs.existsSync(SOURCE_AGENT_DIR) ? '[OK]' : '[FAIL]'}`);
  console.log(`- GEMINI.md: ${fs.existsSync(SOURCE_GEMINI_MD) ? '[OK]' : '[FAIL]'}`);
  console.log(`- .env.example: ${fs.existsSync(SOURCE_ENV_EXAMPLE) ? '[OK]' : '[FAIL]'}`);
  console.log(`- .agent/mcp.json: ${fs.existsSync(MCP_JSON_PATH) ? '[OK]' : '[FAIL]'}`);
  const memDbPath = path.join(SOURCE_AGENT_DIR, 'memory', 'memory.db');
  console.log(`- SQLite memory.db: ${fs.existsSync(memDbPath) ? '[OK]' : '[NOT INITIALIZED]'}`);
  handleMcpList();
}

function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const platform = getPlatform(args);

  // Direct deployment flags (-p, -u, -g) or platform-only flag (e.g. --cursor)
  const knownCommands = ['run', 'answer', 'memory', 'team', 'hitl', 'secure', 'advise', 'graph', 'ask', 'eval', 'worktree', 'dashboard', 'ci', 'doctor', 'mcp', 'install'];
  if (args.includes('-p') || args.includes('--project') || (platform && !knownCommands.includes(args[0]))) {
    let level = 'project';
    if (args.includes('-u') || args.includes('--user')) level = 'user';
    if (args.includes('-g') || args.includes('--global')) level = 'global';
    handleInstall(level, null, dryRun, platform);
    return;
  }
  if (args.includes('-u') || args.includes('--user')) {
    handleInstall('user', null, dryRun, platform);
    return;
  }
  if (args.includes('-g') || args.includes('--global')) {
    handleInstall('global', null, dryRun, platform);
    return;
  }

  const cmd = args[0];
  if (cmd === 'install') {
    let level = 'project';
    if (args.includes('-u') || args.includes('--user')) level = 'user';
    if (args.includes('-g') || args.includes('--global')) level = 'global';
    handleInstall(level, null, dryRun, platform);
  } else if (cmd === 'mcp') {
    handleMcpList();
  } else if (cmd === 'run') {
    const wfRunner = path.join(SOURCE_AGENT_DIR, 'scripts', 'workflow-engine.js');
    if (fs.existsSync(wfRunner)) {
      spawnSync(process.execPath, [wfRunner, ...args], { stdio: 'inherit' });
    } else {
      console.error('[ERROR] workflow-engine.js not found.');
    }
  } else if (cmd === 'answer') {
    const wfRunner = path.join(SOURCE_AGENT_DIR, 'scripts', 'workflow-engine.js');
    if (fs.existsSync(wfRunner)) {
      spawnSync(process.execPath, [wfRunner, ...args], { stdio: 'inherit' });
    }
  } else if (['memory', 'team', 'hitl', 'secure', 'advise', 'graph', 'ask', 'eval', 'worktree', 'dashboard', 'ci'].includes(cmd)) {
    const pythonExe = process.platform === 'win32' ? 'python' : 'python3';
    const cliPy = path.join(__dirname, 'cli.py');
    const res = spawnSync(pythonExe, [cliPy, ...args], { stdio: 'inherit' });
    if (res.error) {
      console.error(`[ERROR] Failed to execute ${cmd} command via python: ${res.error.message}`);
    }
  } else if (cmd === 'doctor') {
    handleDoctor();
  } else {
    console.log('================================================================================');
    console.log('            MEET AI AGENTS - MULTI-AGENT & MCP AUTOMATION PLATFORM              ');
    console.log('================================================================================');
    console.log('Usage:');
    console.log('  meet -p                       # Deploy to current project (./.agent/ & GEMINI.md)');
    console.log('  meet -u                       # Deploy to user profile (~/.gemini/)');
    console.log('  meet -g                       # Deploy to system global level');
    console.log('  meet --cursor                 # Deploy for Cursor IDE (.cursorrules & .cursor/rules/)');
    console.log('  meet --claude                 # Deploy for Claude Code (CLAUDE.md & .mcp.json)');
    console.log('  meet --copilot                # Deploy for GitHub Copilot (.github/)');
    console.log('  meet --codex                  # Deploy for OpenAI Codex (.codex/)');
    console.log('  meet --all                    # Deploy adapters for all platforms');
    console.log('  meet install [--cursor|--claude|--copilot|--codex|--gemini|--all]');
    console.log('  meet mcp list                 # List configured MCP servers & credential readiness');
    console.log('  meet run <workflow>           # Execute workflow automation');
    console.log('  meet answer "<query>"         # Generate structured workflow answer');
    console.log('  meet memory [query|log|sync]  # SQLite persistent memory & context engineering');
    console.log('  meet team board --id <team>   # Shared task board, claiming & peer messaging');
    console.log('  meet hitl list                # Checkpoints awaiting human verification');
    console.log('  meet doctor                   # Run system diagnostics\n');
  }
}

if (require.main === module) {
  main();
}

