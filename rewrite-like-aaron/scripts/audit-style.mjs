#!/usr/bin/env node

import fs from "node:fs";

function usage() {
  console.error(
    "Usage: node audit-style.mjs [--source <original.md>] [--json] <target.md|->",
  );
}

const args = process.argv.slice(2);
let sourcePath = null;
let json = false;
let targetPath = null;

for (let i = 0; i < args.length; i += 1) {
  const arg = args[i];
  if (arg === "--source") {
    sourcePath = args[++i];
  } else if (arg === "--json") {
    json = true;
  } else if (!targetPath) {
    targetPath = arg;
  } else {
    usage();
    process.exit(1);
  }
}

if (!targetPath || (sourcePath === undefined)) {
  usage();
  process.exit(1);
}

function readText(path) {
  if (path === "-") return fs.readFileSync(0, "utf8");
  return fs.readFileSync(path, "utf8");
}

function auditText(raw) {
  const text = raw
    .replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, "")
    .replace(/```[\s\S]*?```/g, "")
    .replace(/`[^`\n]+`/g, "")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/https?:\/\/\S+/g, "")
    .replace(/<[^>]+>/g, "");

  const han = (text.match(/\p{Script=Han}/gu) || []).length;
  const count = (regex) => (text.match(regex) || []).length;
  const markerCounts = Object.fromEntries(
    [
      ["Anyway", /\bAnyway\b/gi],
      ["说白了", /说白了/g],
      ["话说回来", /话说回来/g],
      ["老实说", /老实说/g],
      ["总之", /总之/g],
    ].map(([name, regex]) => [name, count(regex)]),
  );

  const aiPatterns = [
    ["宏大意义", /标志着|彰显|重塑(?:了)?(?:行业|产业|生态|格局)|全新篇章/g],
    ["空泛重要性", /至关重要|不可或缺|深远影响/g],
    ["宣传词", /赋能|无缝|全方位|颠覆性|革命性|强大而直观/g],
    ["假深入", /深入探讨|深刻揭示|充分展现|生动诠释/g],
    ["聊天残留", /希望(?:这|以上).{0,8}(?:有帮助|帮助到你)|如果你(?:还)?需要|请告诉我/g],
    ["通用结尾", /未来可期|让我们拭目以待|迈出.{0,6}重要一步/g],
  ].map(([name, regex]) => ({ name, count: count(regex) }));

  const pairedDashRemoved = text.replace(/——/g, "");
  const paragraphs = text
    .split(/\r?\n\s*\r?\n/)
    .map((p) => p.replace(/^[#>*+\-\d.\s]+/gm, "").trim())
    .filter(Boolean);
  let longestShortRun = 0;
  let shortRun = 0;
  for (const paragraph of paragraphs) {
    const length = (paragraph.match(/\p{Script=Han}/gu) || []).length;
    const oneSentence = (paragraph.match(/[。！？!?]/g) || []).length <= 1;
    if (length > 0 && length < 18 && oneSentence) {
      shortRun += 1;
      longestShortRun = Math.max(longestShortRun, shortRun);
    } else {
      shortRun = 0;
    }
  }

  return {
    han,
    firstPerson: count(/我|自己/g),
    rhetorical: count(/[？?]/g),
    exclamation: count(/[！!]/g),
    boldPairs: Math.floor(count(/\*\*/g) / 2),
    emoji: count(/\p{Extended_Pictographic}/gu),
    contrast: count(
      /不是[^。！？\n]{0,60}而是|不只是[^。！？\n]{0,60}而是|不仅[^。！？\n]{0,60}(?:而且|更)/g,
    ),
    markerCounts,
    markerTotal: Object.values(markerCounts).reduce((sum, value) => sum + value, 0),
    englishDiscourse: count(/\b(?:Anyway|Basically|Honestly|Actually)\b/gi),
    isolatedEmDash: (pairedDashRemoved.match(/—/g) || []).length,
    enDash: count(/–/g),
    asciiPunctuationBetweenCjk: count(
      /\p{Script=Han}[,:;!?]\p{Script=Han}/gu,
    ),
    longestShortRun,
    genericHeadings: count(
      /^#{1,6}\s*(?:挑战与机遇|未来展望|总结与展望|结论)\s*$/gm,
    ),
    aiPatterns,
  };
}

const target = auditText(readText(targetPath));
const source = sourcePath ? auditText(readText(sourcePath)) : null;
const errors = [];
const warnings = [];

if (target.isolatedEmDash > 0) {
  errors.push(`发现 ${target.isolatedEmDash} 个孤立单破折号“—”`);
}
if (target.enDash > 0) {
  errors.push(`发现 ${target.enDash} 个 en dash“–”，区间请使用连字符`);
}
if (target.asciiPunctuationBetweenCjk > 0) {
  errors.push(
    `发现 ${target.asciiPunctuationBetweenCjk} 处夹在中文之间的半角标点`,
  );
}

const markerBudget = Math.min(2, Math.max(1, Math.ceil(target.han / 1000)));
const addedMarkers = source
  ? Math.max(0, target.markerTotal - source.markerTotal)
  : target.markerTotal;
if (addedMarkers > markerBudget) {
  warnings.push(
    `高辨识度口语标记${source ? "净增" : "共有"} ${addedMarkers} 个，建议上限为 ${markerBudget} 个`,
  );
}
for (const [marker, amount] of Object.entries(target.markerCounts)) {
  const original = source?.markerCounts[marker] || 0;
  if (amount - original > 1) {
    warnings.push(`“${marker}”比原稿增加 ${amount - original} 次`);
  }
}

const addedEnglishDiscourse = source
  ? Math.max(0, target.englishDiscourse - source.englishDiscourse)
  : target.englishDiscourse;
if (addedEnglishDiscourse > 1) {
  warnings.push(`英文转场${source ? "净增" : "共有"} ${addedEnglishDiscourse} 个`);
}

const questionBudget = Math.max(1, Math.ceil(target.han / 1500));
const addedQuestions = source
  ? Math.max(0, target.rhetorical - source.rhetorical)
  : target.rhetorical;
if (addedQuestions > questionBudget) {
  warnings.push(
    `问号${source ? "净增" : "共有"} ${addedQuestions} 个，需检查是否在制造探索感`,
  );
}

const contrastBudget = Math.max(1, Math.ceil(target.han / 1000));
const addedContrasts = source
  ? Math.max(0, target.contrast - source.contrast)
  : target.contrast;
if (addedContrasts > contrastBudget) {
  warnings.push(
    `对照句式${source ? "净增" : "共有"} ${addedContrasts} 个，需检查二元结构`,
  );
}

if (target.longestShortRun >= 3) {
  warnings.push(`连续短段最长为 ${target.longestShortRun} 段，需检查金句化节奏`);
}
if (source && target.firstPerson > source.firstPerson + Math.max(3, target.han / 500)) {
  warnings.push(
    `第一人称从 ${source.firstPerson} 增至 ${target.firstPerson}，需逐项核查信息来源`,
  );
}
if (source && target.boldPairs > source.boldPairs + 2) {
  warnings.push(`粗体从 ${source.boldPairs} 处增至 ${target.boldPairs} 处`);
}
if (source && target.emoji > source.emoji) {
  warnings.push(`emoji 从 ${source.emoji} 个增至 ${target.emoji} 个`);
}
if (target.genericHeadings > 0) {
  warnings.push(`发现 ${target.genericHeadings} 个通用结论或展望标题`);
}
for (const pattern of target.aiPatterns) {
  if (pattern.count > 0) {
    warnings.push(`${pattern.name}命中 ${pattern.count} 次`);
  }
}

const result = {
  target: targetPath,
  source: sourcePath,
  metrics: target,
  errors,
  warnings,
};

if (json) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(`Aaron style audit: ${targetPath}`);
  console.log(
    `汉字 ${target.han} · 第一人称 ${target.firstPerson} · 问号 ${target.rhetorical} · 口语标记 ${target.markerTotal}`,
  );
  for (const error of errors) console.log(`[ERROR] ${error}`);
  for (const warning of warnings) console.log(`[WARN] ${warning}`);
  if (errors.length === 0 && warnings.length === 0) {
    console.log("[OK] 未发现表面风格风险");
  }
}

if (errors.length > 0) process.exitCode = 2;
