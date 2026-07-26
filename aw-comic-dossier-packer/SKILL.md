---
name: aw-comic-dossier-packer
description: >-
  End-to-end comic dossier workflow: collect original manga volume cover images,
  optionally upscale them with Gemini/Nano Banana, collect official manga
  introduction text from ACG databases, generate one direct Codex ImageGen
  Xiaohongshu cover card, optionally generate XHS Visual Director cover
  variants when that separate skill is installed, optionally generate a
  humanized Chinese intro when humanizer-zh is installed, and assemble a final
  {manga name}.md with intro, social cards, volume covers, and intro source
  links. Use when the user gives a manga/comic title and wants covers plus a
  summarized introduction and social card output.
metadata:
  author: aaron_xu
  version: "0.1"
  creation_context: "为将漫画封面收集、图片高清化、资料检索、中文介绍整理、小红书视觉生成和最终档案交付整合为可复用工作流而创建。"
---

# AW Comic Dossier Packer

Build one complete manga dossier from a title: cover images, synthesized intro,
Xiaohongshu cover cards, and a final Markdown report.

## Dependencies

Use this skill's bundled scripts as the authoritative implementation for cover
collection and enhancement:

- `scripts/collect_raw_covers.mjs`: fetches original cover images from
  BOOKOF/bookof.moe.
- `scripts/enhance_covers.mjs`: batch-enhances downloaded covers through
  `scripts/nano_banana_upscale.py`.

Optional skills:

- If `humanizer-zh` is available in the Skill catalog or a standard user/project
  Skill directory, read it
  after synthesizing the source-based intro and generate a natural Chinese
  rewrite for the final Markdown. If it is missing, skip the optimized intro
  section and continue.
- If `xhs-visual-director` is available in the Skill catalog or a standard
  user/project Skill directory,
  read it before step 5 and generate optional Xiaohongshu cover variants. If it
  is missing, skip the Visual Director variants and continue with the direct
  ImageGen card only.

Do not edit optional upstream skills. Put all generated work in the current
task output directory, never inside this Skill folder.

## Resolve Directories

Before collecting covers, ask the user to specify the task output directory.
Use an explicit directory from the current request when already provided. If
the user does not specify one, use the current project's repository root; when
there is no repository, use the current working directory. State the resolved
absolute task path before writing.

Resolve `<skill-dir>` as the directory containing this `SKILL.md`. Use it only
to locate bundled scripts. Resolve `<task>` under the selected task output
directory as `manga-social-pack/<safe manga title>`.

## Workflow

1. Collect all original volume cover images from BOOKOF/bookof.moe first.
   - Run:
     `node "<skill-dir>/scripts/collect_raw_covers.mjs" "<漫画名>" --out-dir "<task>/covers"`.
   - If the exact title returns zero results, retry likely aliases before
     giving up: Simplified Chinese, Traditional Chinese, Japanese title, romaji,
     and English title discovered from intro/search results.
   - If search returns multiple matches, show the numbered candidates and rerun
     with `--select N`.
2. After original covers are downloaded, stop and ask: `是否要跳过图片高清化？`
   - This is a blocking user decision. Do not continue to intro collection,
     social-card generation, Markdown writing, or final folder cleanup until the
     user answers, unless the user already gave a clear skip/upscale choice in
     the same request.
   - Include the actual downloaded cover count and a rough Gemini estimate in
     the question. Use about `$0.07 × cover count` for the default 1K path, and
     say actual billing may vary.
   - If yes, keep `covers/` as the final cover folder and do not enhance.
   - If no, enhance the downloaded originals into `covers-enhanced/` with the
     bundled Nano Banana API workflow, not Gemini CLI:
     `node "<skill-dir>/scripts/enhance_covers.mjs" --input-dir "<task>/covers" --out-dir "<task>/covers-enhanced"`.
   - The batch script calls `scripts/nano_banana_upscale.py`, which reads
     `GEMINI_API_KEY` or `GOOGLE_API_KEY` from the environment; if missing, it
     sources `~/.zshrc` and reads the key from there. Never print the key.
   - Default model: `gemini-3.1-flash-image`; API: Google Gemini
     `v1beta/interactions`; default output: `image/jpeg`, `image_size: 1K`.
   - The prompt is technical cover enhancement only: improve clarity and reduce
     compression artifacts while preserving composition, title text, other cover
     text, barcode, colors, and layout. Exception: if the lower-left corner or
     image edge contains a Kmoe/Kmoe-style download-site mark, remove that mark
     cleanly and inpaint the surrounding cover background without adding
     replacement text or new source marks. Do not use Gemini CLI for this step.
   - The script writes `covers-enhanced/enhancement-manifest.json`, tracks exact
     failed covers and reasons, and prints an approximate Gemini cost after each
     run. If a cover fails, keep the best available original only if needed to
     finish the Markdown, and report that volume as requiring manual action.
3. Collect introduction source text from 7 manga database entry pages.
   - Use web search and direct page reads to find 7 reliable entry pages such as
     official publisher pages, MangaDex, MyAnimeList, AniList, Baka-Updates,
     Anime-Planet, Bangumi, or local language manga databases.
   - Read the original intro text from the entry pages, not from a previous
     summary.
   - Use additional web search only as supporting context; the 7 source intros
     remain the required base.
   - Synthesize one copyright-safe Chinese intro of about 400 Chinese
     characters.
4. Optimize the synthesized intro when `humanizer-zh` is installed.
   - If `humanizer-zh` is available, read it before rewriting.
   - Rewrite the synthesized intro to sound more natural and less AI-generated
     while preserving facts, names, genre, premise, and source-grounded claims.
   - Keep the optimized version concise, suitable for a manga dossier, and close
     in information density to the original intro.
   - In the final Markdown, place this text immediately after `## 介绍` under a
     separate heading: `## 介绍（优化后）`.
   - If the skill is not installed, do not invent a humanizer workflow; omit the
     optimized section and report that it was skipped.
5. Generate Xiaohongshu cover cards.
   - Always generate `xhs-02-ai-generated.png` directly with Codex ImageGen at
     Rednote/Xiaohongshu 3:4 ratio. This final PNG must be the ImageGen output
     itself copied into `<task>/social-card/xhs-02-ai-generated.png`.
   - Treat the ImageGen card as a complete original illustrated social cover,
     not a direct reproduction of copyrighted manga cover art or named character
     designs. It may include the manga title, tags, and one short hook, but if
     generated text quality is visibly wrong, report that risk rather than
     replacing the image with an HTML-rendered card.
   - If ImageGen saves the source image under Codex's generated-images folder,
     copy that exact generated image into `social-card/xhs-02-ai-generated.png`
     and leave the original generated-images file in place.
   - If `xhs-visual-director` is available,
     read it and use it as the optional visual-direction layer for Xiaohongshu
     cover generation. Read only the XHS Visual Director references it requires
     for cover style selection, prompt rules, final image generation, and visual
     review.
   - Use the synthesized intro, the optimized intro when available, and one or
     more collected manga cover images as Visual Director input materials.
     Prefer the first volume cover as the image evidence unless another cover
     better represents the work.
   - Generate Visual Director variants as direct ImageGen PNGs. Save every
     generated version directly under `<task>/social-card/` using stable
     filenames such as `xhs-03-visual-director-v01.png`,
     `xhs-03-visual-director-v02.png`, etc. Do not delete weaker attempts or
     intermediate versions; preserve all versions for comparison.
   - For each Visual Director variant, use a distinct visual direction when
     useful, such as source-cover-inspired black/white/red editorial, dark
     emotional magazine cover, or clean collectible manga dossier. Keep all
     variants grounded in the same manga title, tags, and one short hook derived
     from the synthesized intro.
   - After each Visual Director generation, inspect it with Codex vision. Check
     title readability, text errors, missing or duplicated descriptions, QR
     codes/watermarks/buttons, direct imitation of copyrighted cover art or
     named character designs, and whether the cover feels suitable for
     Xiaohongshu 3:4 mobile reading. If a follow-up variant is generated to fix
     an issue, keep both the earlier and later PNG files.
   - If the XHS Visual Director skill is unavailable, tell the user before cover
     production starts: `未检测到 xhs-visual-director；本流程会继续，只生成自带生图封面。`
     Do not stop or wait for installation unless the user explicitly asks to
     install it.
   - Keep the card clean. Optional metadata may include total volume count,
     estimated reading time, author name, or a short label such as `漫画推荐`,
     but these are optional and should be used sparingly. Avoid miscellaneous
     decorative elements, duplicate captions, QR codes, buttons, clutter, and
     unrelated labels.
   - For the direct ImageGen card, prompt for a balanced 3:4 composition:
     left-aligned title/copy when text is requested, a strong central or
     center-left original illustration, and enough visual material on the right
     side to avoid a large empty area. Keep comfortable spacing between the
     image and surrounding text.
   - Final card PNGs must live directly under `<task>/social-card/`:
     `xhs-02-ai-generated.png` always, plus every
     `xhs-03-visual-director-v*.png` produced by the optional Visual Director
     workflow.
6. Create `{漫画名称}.md` in the task folder. The Markdown must contain:
   - `# <漫画名称>`
   - `## 介绍` with the 400-character synthesized intro.
   - `## 介绍（优化后）` immediately after `## 介绍` when `humanizer-zh` was used.
   - `## 封面卡片图` with Markdown image links to every generated social card:
     the direct ImageGen card and every XHS Visual Director variant when
     produced.
   - `## 每卷封面图` with one Markdown image link per volume cover.
   - `## 介绍来源引用` with Markdown links to the 7 intro source entry pages.
   - Do not include a `## 封面来源` section.

## Output Folder

Use a deterministic folder under the user-selected task output directory, or
under the current project directory when the user did not specify one:

```text
manga-social-pack/<safe manga title>/
├── covers/                 # only when upscaling is skipped
├── covers-enhanced/        # only when upscaling is not skipped
├── social-card/
│   ├── xhs-02-ai-generated.png
│   └── xhs-03-visual-director-v*.png  # only when XHS Visual Director is used
└── <漫画名称>.md
```

Use exactly one cover-image folder in the final deliverable:

- If the user skips upscaling, keep `covers/` with original BOOKOF cover images
  and `covers/manifest.json`.
- If the user does not skip upscaling, keep `covers-enhanced/` with only the
  enhanced cover images used by the Markdown.
- Do not keep both `covers/` and `covers-enhanced/` in the final deliverable.
- Do not keep upstream batch roots such as `covers-enhanced-root/`,
  `.tmp-comic-covers/`, raw temporary downloads, duplicate enhanced folders, or
  extra original-image caches after the report is complete.

## Final Report Rules

- Do not paste long copyrighted source introductions into the Markdown.
- Do cite the 7 source entry-page URLs used for the intro.
- Do not include cover-source prose in the final Markdown. Keep cover
  provenance in `covers/manifest.json` or internal notes only.
- Use absolute local image paths in Markdown image tags when reporting results
  to the user in Codex desktop; the file itself may use relative links inside
  the task folder.
- If a source site was not found, write `未找到` for that source and still finish
  the report with available sources.
- If cover enhancement required retries, summarize only the exact volumes and
  reasons. If any cover still failed, explicitly tell the user which image needs
  manual action.
- Before final delivery, clean the task folder so it contains only:
  `{漫画名称}.md`, exactly one of `covers/` or `covers-enhanced/`, and
  `social-card/`. Inside `social-card/`, keep `xhs-02-ai-generated.png` and
  every `xhs-03-visual-director-v*.png` produced. Remove `.DS_Store`,
  `output/`, raw cover caches, and other process artifacts unless the user
  explicitly asked to preserve them. Do not remove Visual Director variants,
  including versions with text or layout issues; report the issue instead.

## Social Card Content Rules

- Main title: the manga title.
- Image: for `xhs-02-ai-generated.png`, use the direct Codex ImageGen output as
  the final card image. For optional XHS Visual Director variants, use collected
  cover art only as high-level visual evidence and prompt context; do not copy
  or reproduce copyrighted cover layouts, logos, barcodes, publisher marks, or
  named character designs directly.
- Tags: 2-4 concise tags that match the manga's real genre or appeal.
- Description: exactly one short Chinese description, derived from the
  synthesized intro. It should feel like a cover hook, not a second synopsis.
- Optional metadata: author, total volumes, estimated reading time, or a short
  label such as `漫画推荐`. Use only what helps the card; omit anything that makes
  the layout noisy.
- Direct ImageGen card prompts must request Rednote/Xiaohongshu 3:4 composition
  and should explicitly avoid watermarks, QR codes, buttons, duplicated
  descriptions, fake logos, and direct imitation of existing manga covers or
  characters.
