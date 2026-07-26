#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_COST_PER_IMAGE_1K = 0.067;

function parseArgs(argv) {
  const args = { inputDir: null, outDir: null, force: false, limit: null, imageSize: '1K', python: 'python3' };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--input-dir') args.inputDir = argv[++i];
    else if (arg === '--out-dir') args.outDir = argv[++i];
    else if (arg === '--limit') args.limit = Number(argv[++i]);
    else if (arg === '--image-size') args.imageSize = argv[++i];
    else if (arg === '--python') args.python = argv[++i];
    else if (arg === '--force') args.force = true;
    else if (arg === '-h' || arg === '--help') args.help = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return args;
}

function usage() {
  return 'Usage: node enhance_covers.mjs --input-dir covers --out-dir covers-enhanced [--image-size 1K] [--limit N] [--force]';
}

async function exists(filePath) {
  try { await fs.access(filePath); return true; } catch { return false; }
}

function isImage(name) {
  return /\.(jpe?g|png|webp)$/i.test(name);
}

function outputStem(name) {
  return path.basename(name, path.extname(name));
}

async function findExistingOutput(outDir, stem) {
  for (const ext of ['.jpg', '.jpeg', '.png', '.webp']) {
    const candidate = path.join(outDir, `${stem}${ext}`);
    if (await exists(candidate)) return candidate;
  }
  return null;
}

function runOne(command, args) {
  return new Promise((resolve) => {
    const child = spawn(command, args, { stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk.toString(); process.stdout.write(chunk); });
    child.stderr.on('data', (chunk) => { stderr += chunk.toString(); process.stderr.write(chunk); });
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.inputDir || !args.outDir) {
    console.log(usage());
    return;
  }
  const inputDir = path.resolve(args.inputDir);
  const outDir = path.resolve(args.outDir);
  await fs.mkdir(outDir, { recursive: true });

  let files = (await fs.readdir(inputDir)).filter(isImage).sort((a, b) => a.localeCompare(b, 'zh-Hans-CN'));
  if (args.limit !== null) files = files.slice(0, args.limit);
  if (files.length === 0) throw new Error(`No images found in ${inputDir}`);

  const script = path.join(__dirname, 'nano_banana_upscale.py');
  const results = [];
  for (const file of files) {
    const input = path.join(inputDir, file);
    const stem = outputStem(file);
    const existing = await findExistingOutput(outDir, stem);
    if (existing && !args.force) {
      console.log(`Skip existing: ${existing}`);
      results.push({ file, status: 'skipped', output: existing });
      continue;
    }
    const out = path.join(outDir, `${stem}.jpg`);
    console.log(`Enhance: ${file}`);
    const commandArgs = [script, '--input', input, '--out', out, '--image-size', args.imageSize, '--force'];
    const result = await runOne(args.python, commandArgs);
    if (result.code === 0) {
      const savedLine = result.stdout.split(/\r?\n/).find((line) => line.startsWith('Saved: '));
      results.push({ file, status: 'enhanced', output: savedLine ? savedLine.slice('Saved: '.length) : out });
    } else {
      results.push({ file, status: 'failed', reason: result.stderr.trim() || result.stdout.trim() || `exit ${result.code}` });
    }
  }

  const manifest = {
    inputDir,
    outDir,
    imageSize: args.imageSize,
    enhancedAt: new Date().toISOString(),
    results,
    costEstimate: estimateCost(results.filter((item) => item.status === 'enhanced').length),
  };
  await fs.writeFile(path.join(outDir, 'enhancement-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);

  const enhanced = results.filter((item) => item.status === 'enhanced').length;
  const failed = results.filter((item) => item.status === 'failed');
  console.log(`Enhanced: ${enhanced}; skipped: ${results.filter((item) => item.status === 'skipped').length}; failed: ${failed.length}`);
  if (enhanced > 0) console.log(`Gemini cost estimate: about $${manifest.costEstimate.usd.toFixed(3)} (${enhanced} image(s), output only; input tokens are usually small).`);
  else console.log('Gemini cost estimate: $0.00 (no new images were enhanced).');
  if (failed.length > 0) {
    console.error('Failed covers:');
    failed.forEach((item) => console.error(`- ${item.file}: ${item.reason.split('\n')[0]}`));
    process.exitCode = 1;
  }
}

function estimateCost(count) {
  return { usd: count * DEFAULT_COST_PER_IMAGE_1K, note: '$0.067 per 1K output image, approximate.' };
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
