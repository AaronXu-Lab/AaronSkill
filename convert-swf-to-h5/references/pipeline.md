# SWF-to-H5 Pipeline

## Contents

1. Intake and source preservation
2. Baseline runtime capture
3. Static inventory
4. Asset and script extraction
5. Obfuscation assessment and recovery
6. Strategy decision
7. Behavioral model
8. Asset preparation
9. Native H5 implementation
10. Differential validation
11. Delivery and cleanup

## 1. Intake and source preservation

Choose a stable `GAME_ID` and create the standard directories:

```bash
GAME_ID="example-game"
mkdir -p "swfs/$GAME_ID" "h5/$GAME_ID" \
  "temp/$GAME_ID/work" "temp/$GAME_ID/validation"
```

Copy original SWFs into `swfs/$GAME_ID/`. Do not edit them in place. Identify the main SWF
and every supplied resource SWF. Record for each file:

- relative filename and role;
- SHA-256 hash;
- known source or acquisition note;
- whether the file is main, preload, resource, language, or level data.

Store this in `swfs/$GAME_ID/manifest.json`. Recompute hashes before delivery.

## 2. Baseline runtime capture

Run the original before reverse engineering it. Prefer a minimal local Ruffle harness with
networking denied unless networking is itself under investigation.

Capture at least:

- loading and title screens;
- help/instructions;
- normal movement and input timing;
- every special mechanic;
- score and item collection;
- death, game over, restart, and completion;
- animation frame order and audio cues;
- visible dimensions and responsive behavior.

Record console errors, network requests, missing files, redirects, and any domain checks.
Put disposable captures in `temp/$GAME_ID/validation/`; promote durable findings to `docs/`
or `h5/$GAME_ID/README.md`.

## 3. Static inventory

Inspect the header:

```bash
python3 tools/scripts/swfhead.py "swfs/$GAME_ID/main.swf"
```

Record compression (`FWS`, `CWS`, or `ZWS`), SWF version, stage size, frame rate, frame count,
and ActionScript generation. `DoABC` indicates AS3; `DoAction`/`DoInitAction` indicates
AS1/AS2.

List top-level tags and exported symbols:

```bash
python3 tools/scripts/swftags.py list "swfs/$GAME_ID/main.swf"
python3 tools/scripts/swfmanifest.py "swfs/$GAME_ID/main.swf"
```

Search decompressed strings for `.swf`, `http`, `.php`, `.aspx`, `loadMovie`,
`sendAndLoad`, and score endpoints. Runtime-loaded resource SWFs are part of the input set;
missing one commonly produces an apparently blank game.

## 4. Asset and script extraction

Set reusable paths:

```bash
SWF="swfs/$GAME_ID/main.swf"
OUT="temp/$GAME_ID/work/extract"
FFDEC="tools/vendor/ffdec/ffdec.jar"
```

Export rendered assets:

```bash
java -jar "$FFDEC" \
  -export image,shape,sprite,frame,text,sound \
  "$OUT/assets" "$SWF"
```

Export source and P-code separately:

```bash
java -jar "$FFDEC" -export script "$OUT/source" "$SWF"
java -jar "$FFDEC" -format script:pcode -export script "$OUT/pcode" "$SWF"
```

Inventory the results rather than copying everything into H5:

- `images/`: embedded bitmaps;
- `shapes/`: vector definitions;
- `sprites/`: MovieClip renders, often the best animation source;
- `frames/`: main timeline renders and scene references;
- `sounds/`: embedded audio;
- `texts/`: static text;
- `scripts/__Packages/`: AS1/2 game classes;
- `scripts/frame_*`: main timeline actions;
- `scripts/DefineSprite_*`: nested timeline actions;
- `scripts/DefineButton2_*`: button actions.

Large sequences of empty main frames usually mean the game is assembled by script with
`attachMovie`; inspect classes and exported symbol names instead of assuming no content.

## 5. Obfuscation assessment and recovery

Search the first source export:

```bash
rg -n '§§push|§§pop|§§constant|invalid_utf8|while\(true\)' "$OUT/source/scripts"
```

For AS1/AS2 with flattened control flow, use the repository's conservative wrapper:

```bash
tools/scripts/decompile-as2.sh "$SWF" "$OUT/deob-safe"
```

It intentionally enables execution-based deobfuscation and constant resolution while
disabling aggressive renaming and deletion. Compare outputs by:

- number of `.as` files;
- method count in the main game class;
- presence of map/item/data classes;
- remaining dispatcher loops;
- semantic readability of key methods;
- P-code constant pools where source looks syntactically valid but nonsensical.

Prefer structurally complete output with a few strange names over clean-looking output that
lost methods. For AS3, use FFDec's AS3 deobfuscation path and compare class structure.

## 6. Strategy decision

Choose one primary delivery strategy:

### Native H5 rewrite

Choose when data and state transitions are recoverable, future modification matters, or the
final package must have no Flash runtime.

### Ruffle shell

Choose when exact fidelity and delivery speed matter more than source-level maintainability.
Inventory external SWFs and block unintended networking. Keep reusable Ruffle tooling under
`tools/vendor/`, and package the required Ruffle runtime and SWFs under the game directory.

### Asset-only extraction

Choose when the request is only to recover art or sound. Do not invent a gameplay rewrite.

Document the decision and its tradeoffs.

## 7. Behavioral model

Before drawing the game, extract a behavioral specification:

- frame rate and fixed-step duration;
- game states and transitions;
- input down/up semantics;
- map generation and difficulty progression;
- movement constants, gravity, speed caps, and scroll speed;
- collision markers and hit shapes;
- scoring formulas and item encodings;
- animation labels and frame ranges;
- sound names and trigger moments;
- persistence and remote calls.

Use named MovieClip markers and placement matrices as authoritative coordinates. Convert all
twips explicitly. Keep a table mapping original names to H5 names.

### Logic provenance ledger

Create the ledger before implementing gameplay and keep it current:

| H5 area | Original behavior | Evidence | Status | Regression |
| --- | --- | --- | --- | --- |
| `updateJump` | `SetGame.gJump_EnterFrame` | AS source + runtime trace | `exact-port` | arc fixture |

Use only these statuses:

- `exact-port`: values, boundary semantics, condition order, and timing are supported by source;
- `equivalent-platform-adaptation`: the browser mechanism differs but observable rules match;
- `intentional-divergence`: the user or standalone-runtime requirements explicitly changed it;
- `unresolved-approximation`: evidence is incomplete or the current behavior is hand-tuned;
- `omitted-original`: an original feature is not present.

For every H5 gameplay method, constant group, input path, timer, sound trigger, persistence path,
and visible state transition, name the original method, timeline, button action, tag geometry, or
runtime capture that supports it. A screenshot resemblance is not enough to mark `exact-port`.
Keep unresolved entries visible in the game README or a durable audit under `docs/`.

## 8. Asset preparation

For every runtime asset:

1. Identify the correct symbol or child sprite, not merely the most obvious exported parent.
2. Record frame count, canvas dimensions, alpha bounding box, and registration point.
3. Inspect a contact sheet for unexpected effects, duplicated frames, clipping, or jitter.
4. If a parent timeline contains a transient sibling effect, export the clean child sprite or
   patch a copy of the SWF/XML under `temp/` and re-export.
5. Preserve originals and keep cleaning reproducible in notes or scripts.
6. Copy only final cleaned files into `h5/$GAME_ID/assets/`.

Do not infer the registration point as `width / 2, height / 2`. Derive it from shape bounds,
timeline matrices, marker clips, or differential pixel coordinates.

## 9. Native H5 implementation

Build a self-contained game directory:

```text
h5/<game>/
  index.html
  game.js or src/
  style.css
  assets/
  tests/
  README.md
```

Implementation order:

1. Create a DOM-independent simulation module or class.
2. Port data tables, constants, and random-selection rules without synthesizing replacements.
3. Port state transitions in the original condition order, including frame boundaries, timers,
   delays, and easing.
4. Add collision with the same Flash `hitTest` overload semantics and original marker geometry.
5. Export the actual animated child timelines and preserve their independent frame counts/rates.
6. Add deterministic tests for state, timing, collision hits, and nearby misses.
7. Add Canvas/WebGL rendering with verified registration offsets.
8. Add input, audio, persistence, responsive scaling, and UI as explicit platform adapters.
9. Remove or localize remote features and record the resulting intentional divergences.

Use a fixed-step accumulator at the SWF frame rate. Make random selection injectable or
seedable for tests. Expose a small debug snapshot containing build version, state, player,
blocks, and active mechanic state.

## 10. Differential validation

Compare original and H5 at the same logical states, not only on the title screen. Validate:

- sprite placement and animation frames;
- visible bitmap edges versus collision edges;
- input timing and state transitions;
- movement arcs and scroll speed;
- sound trigger timing;
- scores, items, difficulty, death, restart, and completion.

Build a failing regression test before fixing a fidelity bug whenever a correct seam exists.
For visual bugs, capture the actual canvas and compare coordinates or pixels; a state-only test
cannot catch a draw-anchor mismatch.

Re-audit the provenance ledger after differential validation. Downgrade any entry that only looks
similar but differs in condition order, timing, collision overload, child animation, or sound
trigger. Do not close an `unresolved-approximation` by silently accepting the H5 behavior.

## 11. Delivery and cleanup

- Run the full checklist in `verification.md`.
- Update the root README and the game README.
- Document intentional differences from the SWF.
- Confirm all runtime requests stay inside `h5/$GAME_ID/`.
- Confirm no runtime file references `temp/`, `swfs/`, or `tools/`.
- Keep permanent tests in H5; leave disposable outputs under ignored `temp/`.
- Verify the game after renaming or temporarily making `temp/$GAME_ID/` unavailable.
