# GitHub Action pins

Retrieved 2026-11-11 from the official repositories. Every external action in `.github/workflows` is pinned to the commit below. The review tag is a comment for humans. A newer release is adopted only by a reviewed change of the workflow, [workflow-governance.json](../operations/workflow-governance.json), and this note together. Do not pin `main`, a floating major tag, or a fork.

The license of each action repository is MIT. The CodeQL CLI bundle that `github/codeql-action` downloads is covered by GitHub's CodeQL terms. That bundle is the action's normal analyzer. It is not a model, tokenizer, or inference runtime.

| Repository | Review tag | Commit | Tag kind | Class | Purpose |
| --- | --- | --- | --- | --- | --- |
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | lightweight | GitHub | Check out the repository without persisting credentials. |
| `astral-sh/setup-uv` | `v10.3.3` | `68559e99cc807c1eb7e9238fd43a15bba460eec2` | lightweight | Astral | Install uv 0.13.0 and select Python 3.12 without a dependency cache. |
| `github/codeql-action` | `v4.39.3` | `33d7b85da1a04171e211befe2c739303b9a4c066` | annotated | GitHub | Initialize and analyze Python. `init` and `analyze` share this commit. |
| `actions/dependency-review-action` | `v5.0.0` | `a1d282b36b6f3519aa1f3fc636f609c47dddb294` | lightweight | GitHub | Fail a pull request on high or critical dependency advisories. |

`actions/checkout` tag `v7.0.1` is the commit itself. `astral-sh/setup-uv` tag `v10.3.3` is the commit itself. `actions/dependency-review-action` tag `v5.0.0` is the commit itself. `github/codeql-action` tag `v4.39.3` is an annotated tag whose commit is `33d7b85da1a04171e211befe2c739303b9a4c066`.

Official sources:

- `https://github.com/actions/checkout`
- `https://github.com/astral-sh/setup-uv`
- `https://github.com/github/codeql-action`
- `https://github.com/actions/dependency-review-action`

`astral-sh/setup-uv` is the official Astral action, not a fork. The workflow input `version: "0.13.0"` is the uv tool release. It is separate from action tag `v10.3.3`. This repository does not use `actions/setup-python`.

Supply-chain rules are in [github-actions-supply-chain.md](../security/github-actions-supply-chain.md).
