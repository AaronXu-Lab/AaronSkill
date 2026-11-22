# Pitfalls and Recovery Tactics

## Contents

1. Decompilation and obfuscation
2. Runtime and black screens
3. Asset export contamination
4. Coordinates, registration, and collision
5. Browser and cache behavior
6. Testing and repository hygiene

## 1. Decompilation and obfuscation

### Default FFDec output can create a false “impossible” verdict

Control-flow flattening appears as `while(true)`, numeric state transitions, `§§push`,
`§§pop`, and `eval("\\x01")`. Raise the AS1/2 execution limit and use conservative
deobfuscation before abandoning a native rewrite.

### Aggressive cleanup can silently delete real behavior

Automatic identifier renaming and removal of “invalid name assignments” reduced the recovered
main class in Flying Ninja Cat from 48 methods to 28. Compare method counts, classes, data
tables, and key transitions across exports. “Fewer weird names” is not a quality metric.

### Constant-pool poisoning produces valid-looking nonsense

Multiple `ConstantPool` instructions in one action block can cause a decompiler to select the
wrong strings. Inspect P-code, substitute each pool, and choose the one that yields coherent
Flash operations such as `_url`, `indexOf`, and `unloadMovie`.

### Unknown tag codes are evidence, not proof

Private or deliberately invalid tags may confuse simple parsers while Flash/Ruffle skips them.
Treat them as a supporting obfuscation signal. Do not strip tags from the original; experiment
only on copies under `temp/`.

## 2. Runtime and black screens

### Missing runtime-loaded SWFs look like renderer failure

Search strings for `.swf` and inspect network 404s. A resource package may provide the title,
preloader, fonts, or assets while the main timeline remains blank.

### Relative loads may resolve against the wrapper page

An AS2 `loadMovie("assets.swf")` can resolve against the embedding document rather than the
main SWF URL in a Ruffle wrapper. Inspect the exact failed request. Set an explicit document
`<base>` or player base URL to the original SWF directory; do not duplicate the resource beside
the wrapper merely to silence the 404.

### A hidden browser tab can stop Ruffle from producing frames

`document.hidden` may throttle `requestAnimationFrame`, leaving a black canvas. Temporarily
replace rAF with a timer to distinguish visibility throttling from broken content:

```javascript
window.requestAnimationFrame = (callback) =>
  setTimeout(() => callback(performance.now()), 16);
```

Remove this diagnostic override afterward.

### Test the renderer before reverse-engineering a domain lock

Set a conspicuous player background color. If the stage changes color, rendering is alive and
the problem is content, script, visibility, or missing resources. Check network and rendered
frames before patching suspected anti-debug logic.

### Empty frame 1 may be normal

Script-driven AS2 games often assemble the screen with `attachMovie` on later frames. Inspect
multiple exported frames and timeline actions before concluding that extraction failed.

### Disable legacy networking deliberately

For a Ruffle shell, deny networking at the player layer. If a binary patch is required, preserve
byte length. Shortening or lengthening a null-terminated ActionScript string can invalidate
constant indexes, action lengths, and jump offsets. Always patch a copy and assert equal length.

## 3. Asset export contamination

### A parent sprite export may bake in an unrelated effect

Flying Ninja Cat's parent character timeline included an `effect_mc` sibling, so every exported
cat frame carried fireworks. Inspect the timeline/XML and contact sheet. Export the clean child
sprite or remove only the unwanted `PlaceObject` from a temporary SWF copy before re-exporting.

### Frame count alone does not prove animation correctness

Nested timelines can duplicate frames or hold a child frame while the parent advances. Compare
alpha bounds and pixels across the sequence, not just filenames and counts.

### A stopped parent label may contain a playing child timeline

AS2 commonly calls `gotoAndStop("run")` on a parent MovieClip while the child placed at that label
continues playing. Exporting the parent's apparent frame range can duplicate stills, omit the last
run frame, or truncate a longer spin cycle. Inspect the labeled frame's placed character, export
that child directly, and preserve the child's own frame count and SWF-rate cadence.

### Idle artwork and its pickup effect may be separate timelines

Do not animate a static item merely because its nested child has multiple frames. In Flying Ninja
Cat the coin stays still; after collection, `id_item` is replaced by a nine-frame sparkle sprite.
Trace the attach/remove actions and export the nested effect as its own sequence.

### Transparent canvas size is not visible content size

Record both PNG dimensions and alpha bounding boxes. Large transparent margins alter naive
centering and can make an otherwise correct sprite appear consistently displaced.

### A flattened composite is not a set of clean layers

An exported progress bar may contain both the track and its initial moving marker. Cropping and
redrawing transparent regions with normal source-over compositing does not erase the baked marker;
transparent pixels leave the old artwork visible. Export the track and marker as separate child
sprites, edit a clean track bitmap, or preserve the original composite. Do not synthesize layers
from one flattened PNG unless the pixel result has been inspected.

### Make user-edited bitmaps easy to hand off

When a user will edit PNGs manually, preserve a canonical runtime asset, state its exact path,
draw origin, scale, and any source crop, and centralize those numbers beside the manifest. Prefer
direct whole-image drawing when practical. Version the bitmap URL after replacement so browser
cache does not mask the edit.

## 4. Coordinates, registration, and collision

### Exported canvas origin is not the MovieClip registration point

A sprite with an 80×56 export is not necessarily centered at `(40, 28)`. Derive the origin from
SWF shape bounds and matrices. In the case study, the hook origin was `(32.75, 15.5)`.

### Logical spacing is not texture width

Flying Ninja Cat used 150px map spacing but a 255px block export centered on the block origin.
Using half the logical width as the image offset moved the building by about 75px. Keep spacing,
draw offset, and collision width as separate constants.

### Visible artwork is not the collision shape

The original used invisible clips such as `ground_pos` and `rope_pos`. Recover their matrices and
shape bounds. Test positive hits and nearby misses. Never replace them with a convenient height
threshold; doing so allowed ropes to attach in empty air.

### Preserve the exact Flash `hitTest` overload

`clip.hitTest(x, y, true)` performs shape-aware point testing, while
`clip.hitTest(otherClip)` uses MovieClip bounds. Recover both transforms and implement the same
overload semantics. Replacing either form with a convenient center/radius circle changes pickups
near corners and edges even when the marker center is correct.

### Recover named markers through the full matrix chain

A marker such as `body.item_pos` may be nested inside several sprites. Read the SWF XML placement
matrices for every parent, compose translation/rotation/scale in order, then convert twips to
pixels. Check every gameplay state that swaps the body sprite. For Flying Ninja Cat, composing the
run/jump matrices located the pickup marker near `(-19.5, -34)` relative to the player, disproving
a convenient center-based collision guess.

### Separate bad spawn data from bad pickup anchors

If an item looks unreachable, compare its generated row/column against the original item table
before expanding collision. Then validate the hidden pickup marker independently. Moving artwork
or enlarging hit radii can hide one error while creating new false-positive pickups. Add one exact
hit and one nearby miss for the recovered anchor, plus a deterministic fixture for the item row.

### Exact item tables outrank plausible procedural patterns

When the SWF contains an `ItemData` table, do not synthesize visually plausible arcs. Index every
layout by its exact map-array signature, copy each block's raw codes, preserve type encodings such
as `<100` versus `>=100`, and compute group bonuses from the same raw layout. Check special map
sequences separately: a finish run may bypass the normal item generator and intentionally contain
no items. Assert table count, map coverage, block alignment, one deterministic layout, and the
special sequence in regression tests.

### The same anchor must feed initialization, drawing, and angle math

Duplicating slightly different hand/rope offsets caused the line and hook to drift. Centralize
registration constants and use them in simulation and rendering. Preserve fixed original angles
for caught or locked states when the SWF explicitly sets one.

### Twips errors are exactly 20×

All tag geometry is in twips. Divide by 20 once at the extraction seam and label converted values
as pixels. Avoid mixing converted and raw coordinates in the same table.

## 5. Browser and cache behavior

### A fixed file does not update an already-running game instance

An old tab can continue executing the pre-fix script indefinitely. A screenshot from that tab may
appear to disprove the patch. Change the script or asset query version, expose a build identifier,
navigate to a unique URL, and verify the loaded build before evaluating behavior.

### Reloading HTML may still retain changed subresources

Version every changed script or binary asset during validation. Confirm the actual request URL and
HTTP status; do not infer success from the address bar.

### Autoplay failure is not an audio asset failure

Browsers reject audio playback before user interaction. Start music on the first valid input and
handle rejected play promises without breaking game initialization.

### Manual random play is a weak reproduction loop

Difficulty gates and random maps can make a bug appear fixed simply because the relevant block
did not spawn. Seed randomness or create a direct simulation fixture that places the required
blocks, items, and player state.

### Similar motion can still have different rules

Condition order, one-frame boundaries, easing functions, and delayed callbacks are gameplay data.
For a death tween or rope swing, port the source statement order and timing before tuning by eye.
Record any smoothing, clamping, elapsed-time cap, or alternate timer as a platform adaptation or
unresolved approximation; do not present it as original logic.

### Unbounded frame preloads can create random local failures

Starting hundreds of `Image` loads in one `Promise.all` can produce intermittent
`ERR_CONNECTION_RESET` failures on a simple local HTTP server. If the failed filename changes
between fresh runs and direct reads return 200, limit the loader to a small worker pool instead of
adding per-file exceptions. Re-test in at least two fresh browser contexts; a warm cache can hide
the race.

## 6. Testing and repository hygiene

### State-only tests miss visual registration bugs

Capture canvas draw arguments, transforms, alpha bounds, or screenshots. Assert that collision
regions overlap the displayed artwork when the bug is visual.

### Keep a real seam for the simulation

Avoid constructing browser globals inside game logic. Accept dependencies and let tests instantiate
the simulation without DOM, audio, or animation loops.

### Do not run prose punctuation formatters over code

Tools that convert half-width punctuation near Chinese text can turn valid calls such as
`foo('中文')` into invalid syntax. Restrict prose formatters to documentation files.

### Preserve originals and unrelated worktree changes

Store experiments under `temp/`, never overwrite source SWFs, and inspect Git status before broad
moves or rewrites. Treat generated images as binary source artifacts unless recompression is an
explicit task.
