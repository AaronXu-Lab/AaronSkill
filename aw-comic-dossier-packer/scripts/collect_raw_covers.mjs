#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';
import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';

const BASE_URL = 'https://bookof.moe';

function parseArgs(argv) {
  const args = { mangaName: null, outDir: 'covers', select: null, limit: null, force: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--out-dir') args.outDir = argv[++i];
    else if (arg === '--select') args.select = Number(argv[++i]);
    else if (arg === '--limit') args.limit = Number(argv[++i]);
    else if (arg === '--force') args.force = true;
    else if (arg === '-h' || arg === '--help') args.help = true;
    else if (!args.mangaName) args.mangaName = arg;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return args;
}

function usage() {
  return 'Usage: node collect_raw_covers.mjs "漫画名" [--out-dir DIR] [--select N] [--limit N] [--force]';
}

function sanitizeFilename(value) {
  return String(value)
    .replace(/[\\/:*?"<>|\r\n\t]+/g, '_')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^[ ._]+|[ ._]+$/g, '') || 'cover';
}

async function requestText(url) {
  const response = await fetch(url, {
    headers: { referer: BASE_URL, 'user-agent': 'Mozilla/5.0' },
  });
  if (!response.ok) throw new Error(`Request failed ${response.status}: ${url}`);
  return response.text();
}

async function requestBytes(url) {
  const response = await fetch(url, {
    headers: { referer: BASE_URL, 'user-agent': 'Mozilla/5.0' },
  });
  if (!response.ok) throw new Error(`Download failed ${response.status}: ${url}`);
  return Buffer.from(await response.arrayBuffer());
}

function postMessages(scriptHtml) {
  return [...scriptHtml.matchAll(/postMessage\(\s*"((?:\\.|[^"\\])*)"/gs)]
    .map((match) => JSON.parse(`"${match[1]}"`));
}

function splitFields(payload, count) {
  const parts = payload.split(',');
  if (parts.length <= count) return parts;
  return [...parts.slice(0, count - 1), parts.slice(count - 1).join(',')];
}

function parseSearchData(dataHtml) {
  const results = [];
  let totalPages = 1;
  for (const message of postMessages(dataHtml)) {
    if (message.startsWith('datainfo-B=')) {
      const [seq, bookId, title, author, updatedAt, cover] = splitFields(message.slice('datainfo-B='.length), 6);
      results.push({ seq, bookId, title, author, updatedAt, cover, href: `${BASE_URL}/b/${bookId}.htm` });
    } else if (message.startsWith('datacount-B=')) {
      const [, , pages] = message.slice('datacount-B='.length).split(',');
      totalPages = Math.max(1, Number(pages) || 1);
    }
  }
  return { results, totalPages };
}

async function searchManga(mangaName) {
  const results = [];
  const seen = new Set();
  let totalPages = 1;
  for (let page = 1; page <= totalPages; page += 1) {
    const parsed = parseSearchData(await requestText(`${BASE_URL}/data_list.php?s=${encodeURIComponent(mangaName)}&p=${page}`));
    totalPages = parsed.totalPages;
    for (const result of parsed.results) {
      if (result.bookId && !seen.has(result.bookId)) {
        seen.add(result.bookId);
        results.push(result);
      }
    }
  }
  return results;
}

async function chooseResult(results, select) {
  if (results.length === 0) return null;
  if (results.length === 1) return results[0];
  console.log(`Found ${results.length} results. Choose one:`);
  results.forEach((result, index) => {
    console.log(`${String(index + 1).padStart(2, ' ')}. ${result.title} | ${result.author} | ${result.bookId}`);
    console.log(`    ${result.cover}`);
  });
  if (select !== null) {
    if (!Number.isInteger(select) || select < 1 || select > results.length) throw new Error(`--select must be between 1 and ${results.length}`);
    return results[select - 1];
  }
  if (!process.stdin.isTTY) throw new Error('Multiple results found. Re-run with --select N.');
  const rl = readline.createInterface({ input, output });
  try {
    while (true) {
      const answer = (await rl.question(`Enter 1-${results.length}, or q to cancel: `)).trim();
      if (['q', 'quit', 'cancel'].includes(answer.toLowerCase())) return null;
      const selected = Number(answer);
      if (Number.isInteger(selected) && selected >= 1 && selected <= results.length) return results[selected - 1];
    }
  } finally {
    rl.close();
  }
}

function findVolumeDataUrl(bookPageHtml) {
  const candidates = [
    ...[...bookPageHtml.matchAll(/https:\/\/bookof\.moe\/data_vol\.php\?h=[^"']+/g)].map((m) => m[0]),
    ...[...bookPageHtml.matchAll(/data_vol\.php\?h=[^"']+/g)].map((m) => `${BASE_URL}/${m[0]}`),
  ];
  const coverCandidates = candidates.filter((candidate) => candidate.includes('VX'));
  const selected = coverCandidates.at(-1) || candidates.at(-1);
  if (!selected) throw new Error('Could not find volume cover data URL.');
  return selected;
}

function parseVolumeData(dataHtml) {
  const covers = [];
  for (const message of postMessages(dataHtml)) {
    if (!message.startsWith('datainfo-V=')) continue;
    const [seq, kind, title, flag, coverUrl] = splitFields(message.slice('datainfo-V='.length), 6);
    covers.push({ seq, kind, title, flag, url: coverUrl });
  }
  return covers;
}

async function getVolumeCovers(bookId) {
  const bookHtml = await requestText(`${BASE_URL}/b/${bookId}.htm`);
  const dataUrl = findVolumeDataUrl(bookHtml);
  return { dataUrl, covers: parseVolumeData(await requestText(dataUrl)) };
}

function extensionFromUrl(url) {
  const ext = path.extname(new URL(url).pathname).toLowerCase();
  return ['.jpg', '.jpeg', '.png', '.webp'].includes(ext) ? ext : '.jpg';
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.mangaName) {
    console.log(usage());
    return;
  }

  console.log(`Searching: ${args.mangaName}`);
  const selected = await chooseResult(await searchManga(args.mangaName), args.select);
  if (!selected) {
    console.log('No cover results found; skipping cover download.');
    return;
  }

  const { dataUrl, covers: allCovers } = await getVolumeCovers(selected.bookId);
  const covers = args.limit !== null ? allCovers.slice(0, args.limit) : allCovers;
  if (covers.length === 0) {
    console.log('No volume covers found.');
    return;
  }

  const root = path.resolve(args.outDir);
  await fs.mkdir(root, { recursive: true });

  const manifest = {
    mangaName: args.mangaName,
    selected,
    bookofPage: selected.href,
    volumeDataUrl: dataUrl,
    covers: [],
  };

  for (const cover of covers) {
    const filename = `${sanitizeFilename(cover.title)}${extensionFromUrl(cover.url)}`;
    const filePath = path.join(root, filename);
    if (!args.force) {
      try {
        await fs.access(filePath);
        console.log(`Skip existing: ${filePath}`);
        manifest.covers.push({ ...cover, file: filePath });
        continue;
      } catch {}
    }
    console.log(`Download: ${cover.title}`);
    await fs.writeFile(filePath, await requestBytes(cover.url));
    manifest.covers.push({ ...cover, file: filePath });
  }

  await fs.writeFile(path.join(root, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
  console.log(`Done: ${root}`);
  console.log(`Manifest: ${path.join(root, 'manifest.json')}`);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
