#!/usr/bin/env node
/**
 * Cross-Platform Node.js Hook Shim for Hyper Agents Force.
 *
 * Bridges IDE hook runners (Claude Code settings.json, Cursor hooks.json, Git hooks)
 * to bin/hook_engine.py with fast JS fallback checks if Python is unavailable.
 */

const path = require('path');
const { spawnSync } = require('child_process');

const SHIELDED_PATTERN = /(^|[\\/])(\.env(\.|$)|id_rsa|id_dsa|id_ed25519|.*\.(pem|key|p12|pfx|kdbx)$)/i;
const INJECTION_PATTERN = /(ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts)|disregard\s+(all\s+)?(system|initial)\s+(rules|prompts)|show\s+me\s+the\s+contents\s+of\s+\.env)/i;

function runFallbackCheck(stage, args) {
  const joined = args.join(' ');
  if (stage === 'pre-prompt' && INJECTION_PATTERN.test(joined)) {
    console.error('[BLOCKED] (pre-prompt) Prompt injection signature detected.');
    process.exit(2);
  }
  if (stage === 'pre-tool' && SHIELDED_PATTERN.test(joined)) {
    console.error('[BLOCKED] (pre-tool) Access to shielded credential file is prohibited.');
    process.exit(2);
  }
  process.exit(0);
}

function main() {
  const args = process.argv.slice(2);
  const stage = args[0] || 'pre-prompt';
  const hookPy = path.join(__dirname, 'hook_engine.py');
  const pythonExe = process.platform === 'win32' ? 'python' : 'python3';

  const res = spawnSync(pythonExe, [hookPy, ...args], {
    stdio: 'inherit',
  });

  if (res.error) {
    runFallbackCheck(stage, args);
    return;
  }

  process.exit(typeof res.status === 'number' ? res.status : 0);
}

if (require.main === module) {
  main();
}
