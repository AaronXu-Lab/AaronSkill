# Base UI Component Source Retrieval

External repository layouts change. Discover the current location before fetching a file, and preserve upstream license notices when copied code requires them.

## Eligibility Gate

Treat eligibility as a property of the exact component variant, not of the library name.

1. Resolve the official documentation, exact preview, registry item, repository, and license.
2. Inspect source imports, `dependencies`, and `registryDependencies`.
3. Accept direct `@base-ui/react` imports, composition from already verified Base UI components, and native React/HTML implementations that do not require another primitive framework.
4. Reject variants that import Radix, React Aria, Ark UI, Headless UI, or another competing component framework. A Base variant elsewhere in the same library is a separate eligible candidate.
5. Record the evidence used: exact path or registry item, relevant imports, dependency findings, and license.

Do not copy source or styling when the license is restrictive or unknown. A clean-room implementation may reproduce only clearly documented observable behavior and accessibility contracts.

## shadcn/ui

The current CLI exposes `docs`, `view`, and `search` commands:

```bash
npx --yes shadcn@latest docs <component>
npx --yes shadcn@latest view <component>
npx --yes shadcn@latest search --query <component>
```

Use `docs` for API and examples and `view` for registry source. Do not run `add` merely to inspect a component because it mutates the project and may install dependencies.

After retrieval:

1. Identify behavior, accessibility contract, composition, and dependencies.
2. Check whether the source uses Radix, Base UI, or native elements; shadcn registry variants may differ.
3. Map behavior to AXO's installed Base UI/native stack.
4. Discard Tailwind styling and external token assumptions.

If the CLI cannot resolve the item, report the exact command/error and verify the official registry before concluding it does not exist.

## coss.com/ui

The coss repository currently stores many components as flat TypeScript files under `packages/ui/src/base-ui/` and `packages/ui/src/components/`. Do not assume `<Name>/index.tsx` exists.

Discover candidates case-insensitively:

```bash
gh api repos/cosscom/coss/git/trees/main?recursive=1 \
  --jq '.tree[].path' \
  | rg -i '^packages/ui/src/(base-ui|components)/.*<name>.*\.(ts|tsx)$'
```

Fetch the exact discovered path:

```bash
gh api "repos/cosscom/coss/contents/<exact-path>" \
  --jq '.content' | base64 -d
```

If the default branch is not `main`, query repository metadata first and substitute its `default_branch`. If no exact component exists, search related primitives or tell the user the source lacks that component.

After retrieval, retain Base UI composition and accessibility behavior that match the requested use case, then replace Tailwind classes and coss-specific utilities with AXO CSS Modules, tokens, and existing utilities.

## Dice UI Base

Use the Base documentation and registry path, never the Radix path:

```text
https://diceui.com/docs/components/base/<name>
https://diceui.com/r/base-vega/<name>.json
```

The registry style is `base-vega`; `/r/base/` currently resolves the Radix source and is not Base UI evidence. Inspect the registry item dependencies and fetched file imports before porting. A component present only under `/docs/components/radix/` or a Radix registry style is not eligible.

## Other Base UI Libraries

Do not require a hardcoded library name. Start from the user-provided or Finder-provided official URL, then locate the official repository and default branch. Search the repository tree for the exact component and inspect rather than install it.

For GitHub repositories:

```bash
gh api repos/<owner>/<repo> --jq '{default_branch,license:.license.spdx_id}'
gh api repos/<owner>/<repo>/git/trees/<default-branch>?recursive=1 --jq '.tree[].path'
gh api repos/<owner>/<repo>/contents/<exact-path> --jq '.content' | base64 -d
```

If the exact source cannot prove Base UI eligibility, stop instead of treating visual similarity as evidence. Do not add the source library as a runtime dependency implicitly.
