# Exemplar patterns — conditional design judgments

Use these patterns to compare ways of expressing the target system's intent. They are alternatives with conditions and trade-offs, not a preferred aesthetic or default tokens. Preserve established choices even when a different pattern could also work. Read this when design examples would help resolve a specific question.

Brand names and source descriptions in external examples are not wording to copy into the contract. Apply the authoring conventions to the resulting design rules.

## Naming & roles

- **Name by intent where hierarchy needs distinct roles.** A surface ladder can distinguish canvas, grouped content, and sunken inputs; another system may keep inputs level and use borders. Name the roles the project actually needs, such as `surface-sunken`, rather than assuming a fixed number or order of surfaces or text levels. Preserve those meanings across supported contexts.
- **Choose how color carries emphasis.** For a quiet operational interface, a restrained accent can make key actions easy to locate; relying on it for every unrelated role can blur meaning. For an expressive presentation, multiple colors or a gradient may carry identity while action emphasis comes from contrast and placement. Define functional, semantic, and decorative roles and the conditions for each. Neither a single accent nor a fixed screen-area percentage is universal.
- **Promote recurring domain colors to first-class tokens.** Chat-bubble roles, compare-slots, KPI gradients are named token families, not ad-hoc hexes. If a color recurs with meaning, it earns a token.

## Theme parity (if multi-theme)

- **Preserve hierarchy across materials.** When multiple themes are established, retain semantic roles while choosing fills, borders, and contrast for each background. A translucent hairline may work on a dark surface but disappear on a light one; a solid neutral border is one alternative, not a required warm-gray palette. Verify the actual composited treatment in each theme's owning artifact; follow the multi-theme storage conventions.
- **Choose the depth cue for the surface.** Tonal steps and borders can keep dense surfaces quiet; shadows can distinguish floating layers but may muddy light surfaces or vanish on dark ones. Select shadow stacks, single drops, or flat separation by the hierarchy needed, then check their effect against the actual background. No shadow recipe is a universal theme default.

## Contrast discipline (ties to the lint `contrast-ratio` rule)

- State the **contrast target per text rung**, and flag the rung that sits below AA: e.g. a `text-dim` tuned to ~3.6:1 clears AA-Large (3:1) but fails AA-Normal (4.5:1) → use only where text actually qualifies as large: at least 24 CSS px regular or approximately 18.67 CSS px bold (18pt / 14pt bold). A 14px regular timestamp is normal text and requires 4.5:1, even when secondary. Record the actual size, weight and background before asserting compliance. See [W3C contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

## Abstracted usage (ties to house rule 3)

- Every component/token entry describes the **shared trait** that makes it apply ("dense, scan-heavy data surfaces", "in-product chrome, not marketing") rather than listing screens. That makes the rule transferable to new components an agent hasn't seen.

## Shape grammar

- **Map shape to the project's roles.** Square or small-radius controls can express precision; pills and circles can emphasize compact actions or touch-oriented controls; larger radii can group content softly. These are possible choices, not guaranteed effects. Define the relationship among role, scale, and shape for the target system. Pill buttons are valid when intentional; mixed radii need clear category or scale distinctions. Check whether a reader can predict the shape of another object with the same role rather than enforcing “pills are only data.”

## Do's & Don'ts that scale

- **Bound additions when identity depends on a closed set.** If the system deliberately limits its palette, explain which roles the set covers and how semantic or content-driven colors fit. An expanding data visualization palette may instead need assignment rules. Do not impose a closed palette merely because an exemplar uses one.
- **Cite tokens, give the reason.** Name the affected token and the observed visual failure a rule prevents, such as a particular translucent border disappearing against its intended background. The reason lets an agent generalize without banning a treatment that works in another context.
- **Treat a signature formula/asset as normative.** If the system computes something (e.g. a score→hue formula), pin it: "treat the formula as a brand asset — don't reskin to buckets, don't add a hue."

## How to use this with the user

Choose only patterns relevant to an unresolved design question. Explain the intended effect, applicable conditions, trade-off, and relationship that should stay consistent. Use existing project decisions without asking the user to choose again. Where evidence is missing, offer a candidate rather than claiming an established rule. Validate the contract with `scripts/check.sh` and the authoring conventions' semantic review; the script does not grade these design judgments.
