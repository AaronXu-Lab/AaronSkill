---
name: aw-logo-finder
description: Find, verify, compare, and export the best brand logo from the brand's official website, HQ ICON, BrandEPS, CDNLogo, Apple App Store, Google Play, and Xiaomi App Store. Use when Codex must locate a company or product logo, favicon, connector icon, or app icon; reject unsuitable aspect ratios and watermarks; prefer authentic high-resolution sources; pause for explicit candidate and output-dimension confirmation; then deliver a verified lossless WebP asset.
metadata:
  author: aaron_xu
  version: "1.0"
---

# AW Logo Finder

Search every source group, compare the actual assets, and stop at the confirmation gate before creating the final WebP.

## Required Source Groups

Treat the groups as independent parallel sources. Do not stop after the first match.

### 1. Official website

Inspect the verified official domain for:

- brand or media-kit downloads;
- square header/product marks;
- `apple-touch-icon`, favicon, and web app manifest icons;
- structured-data organization logos.

Resolve relative asset URLs and inspect the original file, not a search thumbnail. Do not promote a horizontal wordmark merely because it is official.

### 2. Logo resource sites

Search all three:

- HQ ICON: `https://c.subeiz.com/?name={QUERY}&country=cn&entity=software&limit=10&cut=0`
- BrandEPS: `https://brandeps.com/search?s={QUERY}`
- CDNLogo: `https://cdnlogo.com/search?s={QUERY}`

Treat HQ ICON as a logo resource source in this workflow, independently from the application stores below.

### 3. Application stores

Search all three:

- Apple App Store: `https://apps.apple.com/cn/iphone/search`
- Google Play: `https://play.google.com/store/search?q={QUERY}&c=apps`
- Xiaomi App Store: `https://app.mi.com/` using its search UI

Verify an app before accepting its icon:

- app name and product purpose match the requested brand;
- developer/publisher is the brand owner or a verifiable affiliate;
- package/bundle identity, developer website, support link, or privacy-policy domain supports the match;
- the icon is the original highest-resolution artwork, not a screenshot or search thumbnail.

Do not select an app solely because its name matches.

## Candidate Rules

Download or inspect the original candidate and record its URL, file type, pixel dimensions, aspect ratio, transparency, and any watermark.

Reject a candidate when:

- it is clearly not close to square; use a working aspect-ratio range of `0.70–1.43`, and reject obvious wordmarks such as `3237×903`;
- a watermark, site badge, attribution footer, mockup, or screenshot is baked into the image;
- it belongs to a different company, product, seller, or developer;
- it is too small and a higher-resolution authentic version is available;
- it is a deprecated or materially different logo version without evidence that it is still current.

Rank accepted candidates by:

1. verified brand and product identity;
2. agreement with the current official logo or app identity;
3. native resolution and vector availability;
4. closeness to a square composition;
5. clean edges, transparency, and absence of baked backgrounds when those qualities suit the requested use.

Prefer the highest-resolution authentic candidate. Prefer SVG over raster only when it contains the same suitable near-square mark; do not prefer a horizontal vector wordmark over a correct square app icon.

## Comparison Output

Account for all seven sources in one table:

| Source | Found | Candidate | Original size/type | Watermark | Identity evidence | Match | Notes |
|---|---|---|---|---|---|---|---|

Use `Exact`, `Same mark / different treatment`, `Different`, `Rejected`, `Not found`, or `Unavailable` for `Match`.

After the table, provide:

- the recommended candidate and direct source URL;
- why it wins under the candidate rules;
- any material uncertainty or competing variant.

## Mandatory Confirmation Gate

Do not create, convert, resize, or deliver the final WebP before explicit user confirmation.

Ask the user to confirm:

1. the selected candidate;
2. target pixel dimensions, such as `96×96`—use a dimension already supplied by the user instead of asking again;

If the user changes the candidate or output settings, restate the final selection and wait for confirmation when the new instruction is ambiguous. A clear direct selection plus explicit output settings counts as confirmation.

## Produce the WebP

After confirmation, download the verified original and run:

```bash
python3 scripts/prepare_logo.py \
  --input "<source-file>" \
  --output "<brand>-<width>x<height>.webp" \
  --size "<width>x<height>"
```

The script uses lossless WebP by default. Do not ask for a compression target. Honor `--max-kb`, `--quality`, or `--lossless` only when the user explicitly requests a compression mode.

The script rejects clearly non-square inputs, preserves aspect ratio, pads rather than distorts, and prints verification metadata. Use `--background "#FFFFFF"` only when the user requests or the selected source requires an opaque background; otherwise preserve transparency.

Before delivery, verify:

- format is WebP;
- pixel dimensions exactly match the confirmed dimensions;
- file size meets an explicitly requested limit when one exists;
- no watermark or unintended crop was introduced;
- the visible mark still matches the confirmed candidate.

Deliver a clickable file link and report source, dimensions, file size, and compression mode.
