#!/usr/bin/env node

/**
 * Skill Generator & Evaluator Multi-IDE Installer / Uninstaller
 *
 * Supported Workflows:
 *   1. Interactive Installer:
 *      npx github:sarveshtalele/skill-generator-agent-skill install
 *
 *   2. Direct 1-Line IDE Install:
 *      npx github:sarveshtalele/skill-generator-agent-skill install --target claude
 *      npx github:sarveshtalele/skill-generator-agent-skill install --target cursor
 *      npx github:sarveshtalele/skill-generator-agent-skill install --target antigravity
 *      npx github:sarveshtalele/skill-generator-agent-skill install --target windsurf
 *
 *   3. Specific Skill Install:
 *      npx github:sarveshtalele/skill-generator-agent-skill install skill-creator --target claude
 *      npx github:sarveshtalele/skill-generator-agent-skill install evaluator-skill --target cursor
 *
 *   4. Uninstall Skills:
 *      npx github:sarveshtalele/skill-generator-agent-skill uninstall --target claude
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
    desc: 'Audits agent skills on 8 quality dimensions, functional lift, and NVIDIA SkillSpector 17-category AST security.'
  }
];

function printBanner() {
  console.log('\n╔═════════════════════════════════════════════════════════════════════════╗');
  console.log('║       🤖 Skill Generator & Evaluator — Multi-IDE Installer              ║');
  console.log('║   Spec: Agent Skills 1.0  •  Security: NVIDIA SkillSpector 17           ║');
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

function getIdeDestinationPath(target) {
  const home = os.homedir();
  const cwd = process.cwd();

  switch (target.toLowerCase()) {
    case 'claude':
    case 'claude-code':
      return path.join(home, '.claude', 'skills');
    case 'cursor':
      return path.join(cwd, '.cursor', 'skills');
    case 'antigravity':
    case 'gemini':
      return path.join(home, '.gemini', 'antigravity', 'skills');
    case 'windsurf':
      return path.join(cwd, '.windsurf', 'skills');
    case 'github':
    case 'copilot':
      return path.join(cwd, '.github', 'skills');
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

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--target' && args[i + 1]) {
      targetIde = args[i + 1];
      i++;
    } else if (!args[i].startsWith('-') && !['install', 'uninstall', 'list'].includes(args[i])) {
      targetSkill = args[i];
    }
  }

  if (!targetIde) {
    console.log('Select target IDE / Agent environment:');
    console.log('  1. Claude Code (~/.claude/skills/)');
    console.log('  2. Cursor (.cursor/skills/)');
    console.log('  3. Antigravity / Gemini CLI (~/.gemini/antigravity/skills/)');
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

  const destRoot = getIdeDestinationPath(targetIde);
  if (!destRoot) {
    console.error(`❌ Unsupported IDE target: ${targetIde}`);
    process.exit(1);
  }

  const repoDir = ensureRemoteRepoCloned();
  const skillsSourceRoot = path.join(repoDir, 'skills');

  const skillsToInstall = targetSkill
    ? [targetSkill]
    : BUNDLE_SKILLS.map((s) => s.name);

  console.log(`\n🚀 Installing skills into ${targetIde} (\x1b[32m${destRoot}\x1b[0m)...`);

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

  console.log(`\n🎉 Installation complete! The skills are now active in \x1b[32m${targetIde}\x1b[0m.`);
}

async function uninstallSkill(args) {
  printBanner();

  let targetIde = null;
  let targetSkill = null;
  let all = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--target' && args[i + 1]) {
      targetIde = args[i + 1];
      i++;
    } else if (args[i] === '--all') {
      all = true;
    } else if (!args[i].startsWith('-') && !['install', 'uninstall', 'list'].includes(args[i])) {
      targetSkill = args[i];
    }
  }

  if (!targetIde) {
    console.log('Select target IDE to uninstall from:');
    console.log('  1. Claude Code (~/.claude/skills/)');
    console.log('  2. Cursor (.cursor/skills/)');
    console.log('  3. Antigravity (~/.gemini/antigravity/skills/)');
    console.log('  4. Windsurf (.windsurf/skills/)');

    const choice = await prompt('\nEnter choice (1-4): ');
    switch (choice) {
      case '2': targetIde = 'cursor'; break;
      case '3': targetIde = 'antigravity'; break;
      case '4': targetIde = 'windsurf'; break;
      default: targetIde = 'claude'; break;
    }
  }

  const destRoot = getIdeDestinationPath(targetIde);
  if (!destRoot || !fs.existsSync(destRoot)) {
    console.log(`ℹ️ No skills directory found for ${targetIde}.`);
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
