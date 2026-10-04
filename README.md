<p align="center">
  <a href="./README.zh-CN.md">中文 README</a> · <strong>English</strong>
</p>

<p align="center">
  <img src="./assets/readme/hero.en.svg" width="100%" alt="AaronSkill: practical Agent Skills, ready to install">
</p>

<p align="center">
  <strong>Turn real workflows into discoverable, verifiable, reusable Agent Skills.</strong>
</p>

<p align="center">
  Design systems · UI/UX · brand assets · Figma tools · Skill engineering · content workflows
</p>

## Install in one command

```bash
npx skills@latest add AaronXu-Lab/AaronSkill
```

The installer discovers every Skill in the repository that contains a `SKILL.md` and lets you choose which ones to install. To list the available Skills without installing them:

```bash
npx skills@latest add AaronXu-Lab/AaronSkill --list
```

Install one Skill:

```bash
npx skills@latest add AaronXu-Lab/AaronSkill \
  --skill aw-find-and-port-ui-component
```

Install globally for Codex:

```bash
npx skills@latest add AaronXu-Lab/AaronSkill \
  --skill aw-find-and-port-ui-component \
  --agent codex \
  --global
```

> The `skills` CLI installs to the current project by default. Add `--global` to use a Skill across projects. Interactive installation recommends symlinks; use `--copy` to create a standalone copy.

## Skills

### Install local repository symlinks

Run this from the repository to check all first-level Skill directories and create any missing symlinks in `~/.agents/skills`. This includes the Working On and no-longer-maintained Skills.

On macOS, you can also double-click `link-skills.command` in the repository root, then press Return to close the results window when it finishes.

```bash
python3 link-skills.py
```

The script locates the repository relative to itself, so it can run from any working directory. Re-running it skips correct symlinks. It preserves and reports conflicting same-name files, directories, or symlinks that point elsewhere, and exits with code `1`.

Preview changes without writing, or choose another global directory:

```bash
python3 link-skills.py --dry-run
python3 link-skills.py --target ~/.codex/skills
```

The repository currently contains **24 Skills**, grouped by primary purpose into meta Skills, tools, resource discovery, design support, and design agents. It also has a Working On group and a separate list of no-longer-maintained Skills.

### Meta Skill

Capabilities for creating, upgrading, and standardizing other Skills.

| Skill | Version | What it does | Key boundaries |
| --- | --- | --- | --- |
| [`aw-meta-skill`](./aw-meta-skill/) | `1.9.1` | Creates or updates any Skill, serving as the unified entry point in place of `skill-creator` | Reads and validates according to the change scope; Markdown is the source of truth, and SVG details are loaded as needed |

### Tools

Reusable workflows for well-defined inputs and outputs, including asset processing, content handling, and focused engineering tasks.

| Skill | Version | What it does | Key boundaries |
| --- | --- | --- | --- |
| [`aw-logo-asset-cook`](./aw-logo-asset-cook/) | `1.3.1` | Creates and validates cross-platform icon assets from SVGs or images that have been assessed and iteratively redrawn | Requires user-specified input; confirm low-fidelity conversions, and check compatibility and themes after a redraw is approved |
| [`aw-mail-read-later`](./aw-mail-read-later/) | `1.1.1` | Recommends, reads, summarizes, or translates one item from Outlook's `Read Later` folder | Handles one item per manual run; requires confirmation before archiving or removing an email |
| [`aw-tiered-task-dispatch`](./aw-tiered-task-dispatch/) | `1.7.0` | Handles read-only research in the main session and dispatches implementation work in Codex or Claude based on remaining uncertainty, impact, and coordination complexity | Uses the lower tier for settled, local work and the middle tier for substantive design or coordination; clarifies key plans first and treats history only as a weighting signal; resolves the latest available model by series, with user choice taking priority; execution sessions validate independently and do not communicate with each other |
| [`rewrite-like-aaron`](./rewrite-like-aaron/) | `1.1.1` | Rewrites AI-generated Chinese drafts in Aaron's current blog voice | Preserves facts and positions; limits catchphrases, rhetorical questions, and surface-level imitation through Chinese-English mixing |

### Resource discovery

Finds, verifies, filters, and organizes useful resources from external sources.

| Skill | Version | What it does | Key boundaries |
| --- | --- | --- | --- |
| [`aw-comic-dossier-packer`](./aw-comic-dossier-packer/) | `1.1.0` | Collects comic covers, source information, Xiaohongshu covers, and a final dossier | Confirm costs before upscaling; use original visuals rather than reproducing covers in social media graphics |
| [`aw-logo-finder`](./aw-logo-finder/) | `1.1.0` | Finds, compares, and exports brand or product logos from official sites, logo directories, and app stores | Confirm candidates and output dimensions before generating lossless WebP files |

### Design support

Infrastructure, standards, and engineering support for design systems, component implementation, and design delivery.

| Skill | Version | What it does | Key boundaries |
| --- | --- | --- | --- |
| [`aw-design-md-author`](./aw-design-md-author/) | `1.7.0` | Creates, reviews, and maintains complete `DESIGN.md` visual contracts following Google Labs conventions | Protects ownership and comment-only boundaries; reports when official validation is unavailable; does not replace code or Figma |
| [`aw-design-system-gallery`](./aw-design-system-gallery/) | `4.0.0` | Creates, reviews, or improves Gallery default examples, real design axes, and state comparisons | Reuses the local standard structure and documentation layout for component panels; Playground and Properties share axis order, values, and dependency-based disabling; Reset includes theme overrides; section links use path routing and in-page anchors; robustness-only checks do not enter the production Gallery by default; composite examples do not replace child matrices; captions show only real public axes; boundary hints use the existing toggle and both states are verified; project configuration stays in the target repository |
| [`aw-design-fake`](./aw-design-fake/) | `1.8.1` | Unifies fake data, demo source code, and placeholder interactions in prototype projects, and initializes or syncs bundles | Prioritizes real contract data and states; demo scenarios must be explicitly escapable and isolate writes; source code is reused verbatim and displayed without execution; does not touch unit-test mocks |
| [`aw-design-token-consistency-auditor`](./aw-design-token-consistency-auditor/) | `0.9.0` | Compares Figma Variables, `DESIGN.md`, and CSS/Less tokens | Produces audit evidence only and does not rewrite tokens automatically |
| [`aw-find-and-port-ui-component`](./aw-find-and-port-ui-component/) | `2.2.1` | Finds and compares specific components from Base UI and other React sources, including Lobe UI, then adapts them for Base UI and CSS Modules | Handles component-level requests only; Find verifies the exact source and license, then waits for a selection; Port confirms details lost or dependencies added in advance |

### Design agents

Design agents that make interface decisions, conduct reviews, and improve communication quality.

| Skill | Version | What it does | Key boundaries |
| --- | --- | --- | --- |
| [`aw-design-orchestrator`](./aw-design-orchestrator/) | `1.0.0` | Coordinates the AW design workflow from varied requirements through initial UI generation, audits, task walkthrough, and wording review; offers standalone `/help` | Sequential orchestration only; preserves human review and fresh-session handoff; loads stage Skills as needed and reports missing dependencies; no optional enhancements |
| [`aw-design-shaping`](./aw-design-shaping/) | `1.1.0` | Shapes ideas, PRDs, and competitor references into an agreed UI/UX direction through focused questions, research, and wireframes | Users choose the exploration approach and key trade-offs; keeps the initial-generation brief aligned with later approved decisions and implementation status; no exhaustive state coverage or automatic production implementation |
| [`aw-canvas-design`](./aw-canvas-design/) | `1.5.1` | Designs multi-modal business flows on a canvas of real components. `/<business-route>/design-canvas` is the design workspace, and `?preview={name}` walks through one flow. Includes canvas-kit reference components (standalone HTML and React implementations), iterates through comments, and checks route coverage | Reuses the project's existing canvas and dependencies when possible; does not require alignment with a canvas-kit version. The canvas is not a production page and is connected to a real entry point only when explicitly requested |
| [`aw-component-checker`](./aw-component-checker/) | `1.24.1` | Reviews desktop component semantics, composition, and internal usage, and maintains the Component Reference and index | Loads relevant rules as needed; review alone does not rewrite code; not intended for visual-spec checks alone |
| [`aw-ux-info-redundancy-audit`](./aw-ux-info-redundancy-audit/) | `1.7.1` | Audits the information value, semantic duplication, appropriate stage, and visual necessity of UI/UX elements | Reports evidence and a minimal-change decision before implementing interface changes |
| [`aw-flow-completeness-audit`](./aw-flow-completeness-audit/) | `1.1.0` | Audits flow completeness across steps, branches, transitions, handoffs, recovery, and observable outcomes, with evidence and minimal completion proposals | Prioritizes implemented interfaces; records out-of-scope dependencies and unresolved product decisions; requires human review before implementing explicitly approved changes; synchronizes existing design briefs when key decisions change |
| [`aw-task-walkthrough`](./aw-task-walkthrough/) | `1.1.0` | Independently walks through user-selected tasks on interactive prototypes or working products to assess understanding, discoverability, task burden, and outcomes | Runs in a fresh session before wording review; the brief is only a supporting planning reference; may read the full PRD; defaults to a first-time product user who knows the domain; requires real interaction and reports problems with evidence for human review, without proposing fixes or changing the product by default |
| [`aw-wording-reviewer`](./aw-wording-reviewer/) | `0.13.0` | Reviews Simplified Chinese UI typography, terminology, formatting, cross-component data display, and microcopy | Reviews without editing by default; not for English or Japanese, or product information architecture reviews |

Use [`aw-design-orchestrator`](./aw-design-orchestrator/) as the workflow entry point; invoke it with `/help` for a standalone beginner guide.

Recommended sequence: design shaping → initial UI generation with the component library and DESIGN.md → information redundancy audit → component review → flow completeness audit → human review, approved fixes, and rechecks → independent task walkthrough → human review and approved fixes → wording review. Update the existing design brief when approved changes affect key decisions. Wording review retains its consistency rules, including necessary explanatory repetition.

### Working On

Skills under active development, each kept in its own directory for optional installation and use.

| Skill | Version | What it does | Key boundaries |
| --- | --- | --- | --- |
| [`temp-local-service-doctor`](./temp-local-service-doctor/) | `1.1.1` | Starts local multi-service projects and diagnoses port, API, and page-loading failures | Prefers existing entry points; confirms process ownership; verifies through call paths and the target page |
| [`temp-prd-verifier`](./temp-prd-verifier/) | `1.1.1` | Verifies requirements against a project PRD and, when needed, compares them with the interface or implementation | Separates explicit requirements, inferences, and gaps; performs read-only checks or fixes within existing authorization |
| [`temp-small-improves`](./temp-small-improves/) | `1.1.1` | Explicitly checks and improves commonly missed details in interface typography, controls, and motion | Runs only when the user names it; makes the smallest evidence-based changes |

### No longer maintained

These Skills remain in the repository for existing users, but are no longer actively developed or considered for new capabilities.

| Skill | Version | Status |
| --- | --- | --- |
| [`aw-figma-component-governance`](./aw-figma-component-governance/) | `0.10.0` | No longer maintained |

## How these Skills work

```text
Real request
   │
   ├─ Read project, source, and environment constraints
   │
   ├─ Follow a narrow, traceable workflow
   │
   ├─ Pause for confirmation before high-risk or costly actions
   │
   └─ Verify with linting, structured reports, or read-back
```

Skills in this repository put fragile, repetitive steps in `scripts/`, keep rules and schemas in `references/`, and use `SKILL.md` as a clear entry point for execution.

## Repository structure

```text
<skill-name>/
├── SKILL.md              # Trigger guidance and complete workflow
├── scripts/              # Repeatable, deterministic tools (optional)
├── references/           # Schemas, standards, and runbooks (optional)
└── fixtures / graders    # Evaluation assets (optional)
```

The `skills` CLI recursively discovers `SKILL.md` files, so every first-level directory can be installed as an independent Skill.

## Check dependencies before use

Dependencies vary by Skill. Read the relevant `SKILL.md` before invoking one:

- Workflows that use Figma or other external tools require the relevant app, permissions, or authorization.
- Image upscaling requires a Gemini API key and may incur API charges.
- Web research, GitHub source verification, and remote publishing require network access.
- If an optional Skill is unavailable, use a fallback instead of claiming capabilities you do not have.

## Development and validation

After modifying a Skill, at minimum check its frontmatter and directory structure:

```bash
python /path/to/skill-creator/scripts/quick_validate.py ./<skill-name>
```

If the Skill includes scripts, tests, or graders, run the relevant checks too. Successfully loading `SKILL.md` does not mean its workflow has been validated.

## Updates

After installing with the `skills` CLI, update all Skills or a specific Skill:

```bash
npx skills@latest update
npx skills@latest update aw-find-and-port-ui-component
```

See the [`skills` CLI](https://github.com/vercel-labs/skills) for more installation options.
