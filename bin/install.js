#!/usr/bin/env node

/**
 * Skill Generator & Evaluator Multi-IDE Installer / Uninstaller
 *
 * Supported Workflows:
 *   1. Interactive Installer (Prompts for IDE, Scope [Project vs Global], and Project Dir):
 *      npx github:sarveshtalele/skill-generator-agent-skill install
 *
 *   2. Direct 1-Line IDE Install:
 *      npx github:sarveshtalele/skill-generator-agent-skill install --target claude --scope project
 *      npx github:sarveshtalele/skill-generator-agent-skill install --target cursor --dir ./my-app
 *      npx github:sarveshtalele/skill-generator-agent-skill install --target antigravity --global
 *
 *   3. Specific Skill Install:
 *      npx github:sarveshtalele/skill-generator-agent-skill install skill-creator --target claude --scope project
 *      npx github:sarveshtalele/skill-generator-agent-skill install evaluator-skill --target cursor
 *
 *   4. Uninstall Skills:
 *      npx github:sarveshtalele/skill-generator-agent-skill uninstall --target claude --scope global
 *
 *   5. List Bundled Skills:
 *      npx github:sarveshtalele/skill-generator-agent-skill list
 */

import { execSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import readline from 'node:readline';

const REPO_URL = 'https://github.com/sarveshtalele/skill-generator-agent-skill.git';

const BUNDLE_SKILLS = [
  {
    name: 'skill-creator',
    phase: 'Implementation',
    desc: 'Interactive Q&A agent skill creator. Builds Spec 1.0 skills, custom SDD bundles, testing.md checklists & evals.json.'
  },
  {
    name: 'evaluator-skill',
    phase: 'Maintenance & Security',
    desc: 'Audits agent skills on 8 quality dimensions, functional lift, and NVIDIA SkillSpector 68-pattern AST security.'
  }
];

function printBanner() {
  console.log('\n╔═════════════════════════════════════════════════════════════════════════╗');
  console.log('║       🤖 Skill Generator & Evaluator — Multi-IDE Installer              ║');
  console.log('║   Spec: Agent Skills 1.0  •  Security: NVIDIA SkillSpector 68           ║');
  console.log('╚═════════════════════════════════════════════════════════════════════════╝\n');
}

function prompt(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function getIdeDestinationPath(target, scope = 'project', projectDir = process.cwd()) {
  const home = os.homedir();
  const baseDir = scope === 'global' ? home : path.resolve(projectDir);

  switch (target.toLowerCase()) {
    case 'claude':
    case 'claude-code':
      return path.join(baseDir, '.claude', 'skills');
    case 'cursor':
      return path.join(baseDir, '.cursor', 'skills');
    case 'antigravity':
    case 'gemini':
      return scope === 'global'
        ? path.join(home, '.gemini', 'antigravity', 'skills')
        : path.join(baseDir, '.gemini', 'skills');
    case 'windsurf':
      return path.join(baseDir, '.windsurf', 'skills');
    case 'github':
    case 'copilot':
      return path.join(baseDir, '.github', 'skills');
    default:
      return null;
  }
}

function getLocalSkillsSourceDir() {
  const scriptDir = path.dirname(new URL(import.meta.url).pathname);
  const candidate = path.resolve(scriptDir, '..', 'skills');
  if (fs.existsSync(candidate)) return candidate;
  return null;
}

function ensureRemoteRepoCloned() {
  const localDir = getLocalSkillsSourceDir();
  if (localDir) return path.resolve(localDir, '..');

  const tmpDir = path.join(os.tmpdir(), `skill-gen-pkg-${Date.now()}`);
  console.log(`📦 Fetching latest skill bundle from GitHub...`);
  try {
    execSync(`git clone --depth 1 ${REPO_URL} "${tmpDir}"`, { stdio: 'pipe' });
    return tmpDir;
  } catch (err) {
    console.error(`❌ Failed to clone skill repository: ${err.message}`);
    process.exit(1);
  }
}

function copyDirRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function listSkills() {
  printBanner();
  console.log('📋 Available Agent Skills in Bundle:\n');
  BUNDLE_SKILLS.forEach((s, idx) => {
    console.log(`  ${idx + 1}. [${s.phase}] \x1b[36m${s.name}\x1b[0m`);
    console.log(`     ${s.desc}\n`);
  });
}

async function installSkill(args) {
  printBanner();

  let targetSkill = null;
  let targetIde = null;
  let scope = null; // 'project' | 'global'
  let projectDir = process.cwd();

  // Parse CLI arguments
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--target' && args[i + 1]) {
      targetIde = args[i + 1];
      i++;
    } else if (arg === '--scope' && args[i + 1]) {
      scope = args[i + 1].toLowerCase();
      i++;
    } else if (arg === '--global') {
      scope = 'global';
    } else if (arg === '--project') {
      scope = 'project';
    } else if ((arg === '--dir' || arg === '--path') && args[i + 1]) {
      projectDir = args[i + 1];
      scope = scope || 'project';
      i++;
    } else if (!arg.startsWith('-') && !['install', 'uninstall', 'list'].includes(arg)) {
      targetSkill = arg;
    }
  }

  // 1. Select IDE if not specified via CLI
  if (!targetIde) {
    console.log('Select target IDE / Agent environment:');
    console.log('  1. Claude Code (~/.claude/skills/ or .claude/skills/)');
    console.log('  2. Cursor (.cursor/skills/)');
    console.log('  3. Antigravity / Gemini CLI (~/.gemini/antigravity/skills/ or .gemini/skills/)');
    console.log('  4. Windsurf (.windsurf/skills/)');
    console.log('  5. GitHub Copilot (.github/skills/)');

    const choice = await prompt('\nEnter choice (1-5) [default: 1]: ');
    switch (choice) {
      case '2': targetIde = 'cursor'; break;
      case '3': targetIde = 'antigravity'; break;
      case '4': targetIde = 'windsurf'; break;
      case '5': targetIde = 'copilot'; break;
      default: targetIde = 'claude'; break;
    }
  }

  // 2. Select Installation Scope if not specified via CLI
  if (!scope) {
    console.log('\nSelect installation scope:');
    console.log(`  1. Project-level  -> Install inside a specific project/repository [Recommended]`);
    console.log(`  2. Global-level   -> Install in user home directory (available across all projects)`);

    const scopeChoice = await prompt('\nEnter choice (1-2) [default: 1]: ');
    scope = scopeChoice === '2' ? 'global' : 'project';
  }

  // 3. Prompt for Project Directory if scope is project
  if (scope === 'project' && !args.includes('--dir') && !args.includes('--path')) {
    const cwdDisplay = process.cwd();
    const customDir = await prompt(`\nEnter project directory [default: ${cwdDisplay}]: `);
    if (customDir && customDir.trim()) {
      projectDir = path.resolve(customDir.trim());
    }
  }

  const destRoot = getIdeDestinationPath(targetIde, scope, projectDir);
  if (!destRoot) {
    console.error(`❌ Unsupported IDE target: ${targetIde}`);
    process.exit(1);
  }

  const repoDir = ensureRemoteRepoCloned();
  const skillsSourceRoot = path.join(repoDir, 'skills');

  const skillsToInstall = targetSkill
    ? [targetSkill]
    : BUNDLE_SKILLS.map((s) => s.name);

  console.log(`\n🚀 Installing skills into ${targetIde} (\x1b[33m${scope.toUpperCase()}\x1b[0m scope):`);
  console.log(`   Destination: \x1b[32m${destRoot}\x1b[0m\n`);

  for (const skillName of skillsToInstall) {
    const src = path.join(skillsSourceRoot, skillName);
    const dest = path.join(destRoot, skillName);

    if (!fs.existsSync(src)) {
      console.warn(`⚠️ Skill '${skillName}' not found in bundle, skipping.`);
      continue;
    }

    copyDirRecursive(src, dest);
    console.log(`  ✅ Installed \x1b[36m${skillName}\x1b[0m -> ${dest}`);
  }

  console.log(`\n🎉 Installation complete! The skills are now active in \x1b[32m${targetIde}\x1b[0m (${scope} scope).`);
}

async function uninstallSkill(args) {
  printBanner();

  let targetIde = null;
  let targetSkill = null;
  let scope = null;
  let projectDir = process.cwd();

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--target' && args[i + 1]) {
      targetIde = args[i + 1];
      i++;
    } else if (arg === '--scope' && args[i + 1]) {
      scope = args[i + 1].toLowerCase();
      i++;
    } else if (arg === '--global') {
      scope = 'global';
    } else if (arg === '--project') {
      scope = 'project';
    } else if ((arg === '--dir' || arg === '--path') && args[i + 1]) {
      projectDir = args[i + 1];
      scope = scope || 'project';
      i++;
    } else if (!arg.startsWith('-') && !['install', 'uninstall', 'list'].includes(arg)) {
      targetSkill = arg;
    }
  }

  if (!targetIde) {
    console.log('Select target IDE to uninstall from:');
    console.log('  1. Claude Code');
    console.log('  2. Cursor');
    console.log('  3. Antigravity / Gemini CLI');
    console.log('  4. Windsurf');
    console.log('  5. GitHub Copilot');

    const choice = await prompt('\nEnter choice (1-5): ');
    switch (choice) {
      case '2': targetIde = 'cursor'; break;
      case '3': targetIde = 'antigravity'; break;
      case '4': targetIde = 'windsurf'; break;
      case '5': targetIde = 'copilot'; break;
      default: targetIde = 'claude'; break;
    }
  }

  if (!scope) {
    console.log('\nSelect scope to uninstall from:');
    console.log('  1. Project-level');
    console.log('  2. Global-level');

    const scopeChoice = await prompt('\nEnter choice (1-2) [default: 1]: ');
    scope = scopeChoice === '2' ? 'global' : 'project';
  }

  if (scope === 'project' && !args.includes('--dir') && !args.includes('--path')) {
    const cwdDisplay = process.cwd();
    const customDir = await prompt(`\nEnter project directory [default: ${cwdDisplay}]: `);
    if (customDir && customDir.trim()) {
      projectDir = path.resolve(customDir.trim());
    }
  }

  const destRoot = getIdeDestinationPath(targetIde, scope, projectDir);
  if (!destRoot || !fs.existsSync(destRoot)) {
    console.log(`ℹ️ No skills directory found at ${destRoot}.`);
    return;
  }

  const skillsToRemove = targetSkill
    ? [targetSkill]
    : BUNDLE_SKILLS.map((s) => s.name);

  console.log(`\n🗑️ Removing skills from ${targetIde} (${destRoot})...`);
  for (const skillName of skillsToRemove) {
    const targetDir = path.join(destRoot, skillName);
    if (fs.existsSync(targetDir)) {
      fs.rmSync(targetDir, { recursive: true, force: true });
      console.log(`  🗑️ Removed \x1b[31m${skillName}\x1b[0m`);
    }
  }

  console.log(`\n✅ Uninstallation complete.`);
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'install';

  switch (command) {
    case 'list':
      listSkills();
      break;
    case 'uninstall':
      await uninstallSkill(args);
      break;
    case 'install':
    default:
      await installSkill(args);
      break;
  }
}

main().catch((err) => {
  console.error(`\n❌ Error: ${err.message}`);
  process.exit(1);
});
