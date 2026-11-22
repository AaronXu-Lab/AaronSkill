# Convert SWF to H5

This document defines the workflow. Its visual overview is [the workflow diagram](../docs/workflow.svg).

Produce a maintainable H5 game while preserving the original SWF and enough evidence to
verify behavior. Treat conversion as reverse engineering plus differential validation, not
as a blind asset export.

Apply this workflow to SWFs and game assets the user owns or has permission to port. Run project-relative commands from the target game repository. The example helper scripts and workspace layout are provided by [Anti-SWF](https://github.com/AaronXu-Lab/Anti-SWF). Set up the necessary local tools before running the examples.

## Required repository layout

Use a stable lowercase kebab-case `GAME_ID`:

```text
swfs/<game>/                 immutable inputs and manifest.json
h5/<game>/                   standalone final runtime and permanent tests
temp/<game>/work/            disposable FFDec output and experiments
temp/<game>/validation/      disposable screenshots and reports
docs/                        durable findings
tools/scripts/               repository-owned tooling
tools/vendor/                FFDec, Ruffle, and other third-party tools
```

Never mutate an original SWF. Keep the native H5 runtime independent of `temp/`, `swfs/`, Ruffle, and reverse-engineering tools. A Ruffle shell delivers its declared runtime and authorized SWF as separate dependencies.

For an asset-only request, preserve inputs, extract and check the requested assets, and report their paths and provenance. The game-delivery gates apply to native ports and Ruffle shells.

## Read the references in phase order

1. Before starting or choosing an implementation strategy, read
   [references/pipeline.md](pipeline.md) completely.
2. Before changing exported assets, coordinate math, collision, networking, or a black
   screen, read [references/pitfalls.md](pitfalls.md) completely.
3. Before claiming the conversion complete, read and execute
   [references/verification.md](verification.md) completely.

## Operating rules

### Establish a baseline first

- Record SHA-256 hashes, SWF version, ActionScript generation, stage size, frame rate, and
  frame count before modifying anything.
- Run the original in an isolated Ruffle page when possible. Capture title, gameplay,
  jump, special mechanics, death, restart, and audio behavior.
- Inspect console and network requests. Locate runtime-loaded SWFs and remote score or
  tracking endpoints before selecting an architecture.

### Decide instead of assuming

- Prefer a native Canvas/WebGL rewrite when logic and data can be recovered and the goal
  is a maintainable, standalone game.
- Use a Ruffle shell when byte-level fidelity or delivery time dominates and maintenance
  of the original behavior is acceptable.
- Do not interpret heavy obfuscation as proof that native H5 is impossible. Run the
  conservative deobfuscation workflow and compare structural completeness first.

### Port before inventing

- Treat the original SWF as the behavioral specification. Before authoring logic, exhaust
  recovered AS source, P-code, main and nested timeline actions, button actions, exported
  symbols, placement matrices, hidden markers, and baseline runtime captures.
- Maintain a provenance ledger for every gameplay rule and user-visible flow. Classify each
  entry as `exact-port`, `equivalent-platform-adaptation`, `intentional-divergence`,
  `unresolved-approximation`, or `omitted-original` and record the evidence and regression test.
- Preserve original data, formulas, condition order, frame timing, easing, random-selection
  rules, collision semantics, animation child-frame counts, sound triggers, and state
  transitions. JavaScript structure may differ; observable rules may not.
- Do not replace recoverable behavior with plausible procedural patterns, convenient hit
  radii, hand-tuned motion, generic UI flows, or invented timing. If evidence is incomplete,
  isolate the provisional behavior, label it as an approximation, and do not call it restored.
- Add browser-only behavior only when the platform requires it or the user requests it. Keep
  the original rule underneath the adapter when possible and document every intentional change.
- Audit the finished H5 method-by-method against the provenance ledger before claiming fidelity.

### Build from data and state

- Extract data tables before rendering code: maps, item layouts, scores, difficulty,
  speeds, gravity, frame labels, and exported symbol names.
- Write an explicit state machine for gameplay states. Keep simulation independent from
  DOM and rendering so tests can drive it deterministically.
- Use the SWF frame rate as a fixed simulation step. Render with `requestAnimationFrame`,
  but do not make physics depend directly on variable display intervals.
- Convert twips to pixels explicitly: `20 twips = 1 px`.

### Treat registration points as source data

- Do not center every PNG by width and height. FFDec PNG bounds describe the exported
  canvas, not necessarily the MovieClip registration point.
- Derive draw offsets from SWF matrices, shape bounds, named marker clips, or a validated
  old/new pixel comparison.
- Derive collision from the original hidden markers (`ground_pos`, `rope_pos`, hit shapes)
  rather than visible bitmap dimensions.
- Add positive-hit and nearby-miss regression tests whenever collision changes.

### Keep the runtime self-contained

- Copy only cleaned, required images and audio into `h5/<game>/assets/`.
- Use relative runtime paths rooted in the game directory.
- Remove or replace remote submissions and tracking unless explicitly required.
- Respect browser autoplay restrictions and degrade safely when audio playback is denied.
- Version changed scripts and exported assets during browser validation; verify the loaded
  build identifier rather than trusting a reload.

## Completion contract

Do not report success until all of the following are true:

- The original SWF hashes still match the manifest.
- Applicable package tests and syntax checks pass. For a Ruffle shell, verify its bundled runtime and SWF load in the target browser.
- Browser network requests contain no 404s or unintended remote calls.
- Key states match the original visually and behaviorally.
- A fresh-cache browser loads the intended build.
- The chosen delivery still runs when `temp/<game>/` is unavailable.
- The game README documents controls, known intentional differences, and verification
  commands.

Preserve small permanent regression tests under `h5/<game>/tests/`. Keep one-off screenshots
and decompiler output under `temp/` so they can be deleted after delivery.
