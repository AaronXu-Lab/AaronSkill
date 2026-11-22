# Conversion Verification

## Contents

1. Source integrity gate
2. Extraction quality gate
3. Asset fidelity gate
4. Simulation gate
5. Browser gate
6. Standalone delivery gate
7. Completion report

Run every applicable gate. A title screen rendering successfully is not conversion completion.

## 1. Source integrity gate

- Verify every original input is under `swfs/<game>/`.
- Verify `manifest.json` is valid JSON and lists every runtime resource SWF.
- Recompute SHA-256 hashes and compare with the manifest.
- Confirm no original SWF was patched in place.

Example:

```bash
python3 -m json.tool "swfs/$GAME_ID/manifest.json" >/dev/null
shasum -a 256 "swfs/$GAME_ID"/*.swf
```

## 2. Extraction quality gate

- Record SWF header facts with `swfhead.py`.
- Count exported scripts and methods in key classes.
- Confirm map, item, sound, input, and main-loop classes are present.
- Search for residual flattened dispatchers and invalid identifiers.
- Compare conservative and aggressive exports if deobfuscation was required.
- Inspect P-code when source semantics remain incoherent.

Do not accept an export solely because FFDec exited successfully.

## 3. Asset fidelity gate

For each animation family or UI asset:

- verify expected frame count;
- verify pixel dimensions;
- compute or inspect alpha bounding boxes;
- inspect a contact sheet for contaminating layers and clipping;
- verify frame order and duplicate/held frames against the original timeline;
- record the draw registration point separately from image dimensions;
- ensure images and audio needed at runtime live under `h5/<game>/assets/`.

Include targeted regression tests for any asset that previously failed.

## 4. Simulation gate

Test the gameplay model without relying on manual timing:

- every state transition, including cancel/failure paths;
- fixed-step physics constants and caps;
- map generation at each difficulty;
- item placement, scoring, group bonuses, and progression;
- ground and special collision with positive and nearby-negative cases;
- death, restart, completion, and persistence;
- no remote submission when networking is intentionally removed.

Make randomness injectable or seeded. A test fixture must be able to place a player and map block
at exact coordinates.

Run game-specific checks, for example:

```bash
node "h5/$GAME_ID/tests/rope.test.cjs"
node --check "h5/$GAME_ID/game.js"
git diff --check
```

Adapt filenames to the game; do not skip equivalent checks because the example differs.

## 5. Browser gate

Start a local server from the repository root:

```bash
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/h5/<game>/` in a fresh-cache browser and verify:

- expected build identifier and versioned script URL;
- no console errors;
- no failed image, audio, script, or font requests;
- no unintended remote network requests;
- pointer, touch, and keyboard controls as applicable;
- audio starts after interaction and failure is non-fatal;
- responsive scaling preserves aspect ratio and input coordinates;
- hidden/visible tab behavior is acceptable.

Exercise at least these states:

| State | Verify |
| --- | --- |
| Load/title | all resources loaded, UI aligned |
| Help | navigation, text, buttons |
| Normal play | movement, ground, scrolling, items |
| Special mechanic | positive hit, miss, release/cancel |
| Death | animation, sound, score, transition |
| Restart | state fully reset |
| Completion | final state and score |

Capture visual evidence for registration or collision fixes. Verify that a hit point coincides with
the currently visible target, not only a logical object in state.

## 6. Standalone delivery gate

Search runtime files for forbidden dependencies:

```bash
rg -n 'temp/|swfs/|tools/' "h5/$GAME_ID" \
  --glob '!README.md' --glob '!tests/**'
```

The command should return no runtime references. Also verify:

- all paths are relative to `h5/<game>/`;
- the game works without Ruffle unless Ruffle is the chosen delivery strategy;
- the game does not require decompiler output;
- the game still loads after `temp/<game>/` is renamed or absent;
- README documents controls, run command, tests, and intentional differences;
- disposable screenshots and reports remain under ignored `temp/`;
- permanent regression tests remain under `h5/<game>/tests/`.

## 7. Completion report

Report:

- chosen strategy and why;
- original inputs and verified hashes;
- final H5 entry URL/path;
- tests and browser states exercised;
- intentional deviations from the SWF;
- remote features removed or retained;
- known limitations;
- confirmation that `temp/<game>/` is not required.

If any gate is incomplete, say which one and do not describe the conversion as finished.
