# UI Component Source Retrieval

External repository layouts and supported variants change. Discover the current source before fetching a file, and preserve upstream license notices when copied code requires them.

## Eligibility and Compatibility Gate

Treat eligibility as a property of the exact component variant, not of the library name.

1. Resolve the official documentation, exact preview, registry item, repository, default branch, and license.
2. Inspect source imports, package dependencies, registry dependencies, peer dependencies, required providers, and styling or token tools. A source-level type or catalog hint is not proof of the exact component's foundation.
3. Separate dependencies that are part of the required behavior from source implementation choices that can be replaced. Compare the required behavior with the target project's React, Base UI, CSS Modules, versions, build system, components, and tokens.
4. Mark a variant suitable for Port only when its required behavior and user-specified details can be recreated in the target Base UI + CSS Modules stack, or when the user has approved a concrete unavoidable addition or deviation. Source use of another foundation or styling tool alone does not make it unsuitable.
5. Record exact evidence: source path or registry item, relevant imports, dependencies to keep or replace, license, conversion risk, and compatibility conclusion.

Do not permanently classify a whole library from one incompatible variant. Recheck current variants when upstream sources change.

Do not copy source or styling when the license is restrictive or unknown. A clean-room implementation may reproduce only clearly documented observable behavior and accessibility contracts.

## Retrieval Workflow

Prefer read-only inspection. Do not run an install or add command merely to inspect a component.

For GitHub repositories:

```bash
gh api repos/<owner>/<repo> --jq '{default_branch,license:.license.spdx_id}'
gh api repos/<owner>/<repo>/git/trees/<default-branch>?recursive=1 --jq '.tree[].path'
gh api repos/<owner>/<repo>/contents/<exact-path> --jq '.content' | base64 -d
```

For Lobe UI, start with the [official component documentation](https://ui.lobehub.com/) or its [component index](https://ui.lobehub.com/llms.txt), then verify the selected variant in [lobehub/lobe-ui](https://github.com/lobehub/lobe-ui). Check the repository's [LICENSE](https://github.com/lobehub/lobe-ui/blob/master/LICENSE) at the same revision as the source before copying code. The catalog's `mixed` and `antd-style` labels are discovery hints; inspect the exact component and its imports, providers and styling rather than treating the whole library as one implementation.

For registry-based sources:

1. Fetch the exact registry item.
2. Inspect every included file and declared dependency.
3. Follow registry dependencies until their foundations are known.
4. Distinguish documentation variants that share a component name but use different foundations.

If the source CLI provides read-only documentation, view, or search commands, prefer those over mutating add/install commands.

## Adaptation Evidence

After retrieval, identify:

- required behavior and states;
- accessibility semantics and keyboard behavior;
- component composition;
- controlled and uncontrolled APIs;
- dependencies and providers;
- styling and token assumptions;
- optional complexity that the current use case does not require.

Use these findings for the selected phase: [Find comparison](find.md) or [Port adaptation](port.md). Read only that phase; source retrieval does not switch phases.

Stop when the exact source cannot be verified, the license does not permit the intended use, or the proposed conversion would require an unapproved detail loss or dependency.
