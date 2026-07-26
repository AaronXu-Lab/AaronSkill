# UI Component Source Retrieval

External repository layouts and supported variants change. Discover the current source before fetching a file, and preserve upstream license notices when copied code requires them.

## Eligibility and Compatibility Gate

Treat eligibility as a property of the exact component variant, not of the library name.

1. Resolve the official documentation, exact preview, registry item, repository, default branch, and license.
2. Inspect source imports, package dependencies, registry dependencies, peer dependencies, and required providers.
3. Compare those requirements with the target project's actual framework, component foundation, version constraints, build system, and styling approach.
4. Mark a variant compatible only when it can use the project's existing stack or when the user explicitly approves the required additions.
5. Record exact evidence: source path or registry item, relevant imports, dependency findings, license, and compatibility conclusion.

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

Map these findings to the target project's installed stack. Reuse existing components and utilities where their public contract fits. If `DESIGN.md` exists, use its owned visual rules as style guidance while respecting implementation details owned by code.

Stop when the exact source cannot be verified, the license does not permit the intended use, or compatibility would require an unapproved foundational dependency.
