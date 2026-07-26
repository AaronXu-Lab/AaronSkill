# Exemplar patterns — transferable conventions from a gold-standard DESIGN.md

Distilled from a high-quality real-world DESIGN.md (a dual-theme developer-console design system). These are *reusable design judgments* to reach for while authoring — not values to copy. Read this when the user wants examples of "what good looks like."

> Caveat: the source document names its product in body prose. That conflicts with the house rule "no product/brand name in the markdown body." Treat the structural patterns below as exemplary; keep following the house rule on naming.

## Naming & roles

- **Name by intent, build ladders.** Colors form a *surface ladder* (`bg` → `bg-deep` → `bg-card` → `bg-card2`) with stable semantics: inputs sit *below* cards (read as "wells"), hover sits *above*. Text is a 3-step ladder (`text` / `text-muted` / `text-dim`). Naming the rung by its role lets the same token carry across themes/contexts.
- **One brand constant, rationed.** A single accent carries every conversion target (CTA, active nav, focus ring, wordmark) and is kept under ~10% of any screen. Everything else stays low-voltage so it reads.
- **Promote recurring domain colors to first-class tokens.** Chat-bubble roles, compare-slots, KPI gradients are named token families, not ad-hoc hexes. If a color recurs with meaning, it earns a token.

## Theme parity (if multi-theme)

- **Parity, not translation.** A light theme is not the dark theme re-tinted. Each surface needs *different materials* to produce the *same hierarchy*: e.g. dark uses translucent-accent hairlines on near-black (the luminance step does the work); light uses **solid warm-grey hex** hairlines on cream (a translucent tint would composite to invisible on white). Define both values in the same commit; a token without its pair will fall back and break one theme.
- **Shadows are theme-specific material.** Near-black eats soft shadows → single deep drop; light surfaces → a two-stop stack tinted with the same ink as the body text (not slate), so cards lift without a cool smudge.

## Contrast discipline (ties to the lint `contrast-ratio` rule)

- State the **contrast target per text rung**, and flag the rung that sits below AA: e.g. a `text-dim` tuned to ~3.6:1 clears AA-Large (3:1) but fails AA-Normal (4.5:1) → reserve for ≥14px non-essential metadata, and say so explicitly in the token's prose and in Do's/Don'ts. Never let a sub-AA color carry essential text.

## Abstracted usage (ties to house rule 3)

- Every component/token entry describes the **shared trait** that makes it apply ("dense, scan-heavy data surfaces", "in-product chrome, not marketing") rather than listing screens. That makes the rule transferable to new components an agent hasn't seen.

## Shape grammar

- **Each radius signals a category, stated as a positive rule** (not an exception): small radius = interactive controls; medium = cards; full-pill = *data* (badges/chips/scores). "Pills are for data, sm/md radii are for interactive containers" — so mixing them on one row is a grammar break.

## Do's & Don'ts that scale

- **Closed sets.** "The palette is closed at [these hues] + the dynamic score — new accents flatten the voice." A closed-set rule scales better than per-case approvals.
- **Cite tokens, give the reason.** Each rule names the token and the visual failure it prevents ("don't use translucent accent for light hairlines — it composites to invisible on white"). The *why* is what lets an agent generalize.
- **Treat a signature formula/asset as normative.** If the system computes something (e.g. a score→hue formula), pin it: "treat the formula as a brand asset — don't reskin to buckets, don't add a hue."

## How to use this with the user

Offer these as menus of judgment when they're stuck on a section ("for elevation, do you want a single deep drop or a stacked lift? here's the trade-off"), not as values to paste. The point is to help them make *their* call consistently, then validate with `scripts/check.sh`.
