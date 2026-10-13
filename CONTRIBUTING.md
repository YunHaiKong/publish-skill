# Contributing

Thanks for considering a contribution to `publish-skill`, the WorkBuddy skill publisher.

## What this repo does

Bundles a WorkBuddy skill that runs `scripts/publish_skill.py` to take a skill directory all the way from local source to a public GitHub repo + marketplace-ready zip, in one command.

## Repo layout

```
SKILL.md                      # WorkBuddy skill entry point
scripts/publish_skill.py      # The publisher itself
references/                   # Loaded by the agent at runtime
assets/                       # SVGs and demo
skill-publisher.zip           # Distributable bundle
.github/
  workflows/lint.yml          # Pyflakes-style syntax check on push
```

## Workflow for code changes

1. Fork the repo.
2. Branch: `git checkout -b feature/your-change`.
3. Edit `scripts/publish_skill.py`. Avoid adding new dependencies — the script must stay stdlib-only (`argparse`, `pathlib`, `subprocess`, `sys`, `os`).
4. Test locally:
   ```bash
   python scripts/publish_skill.py --help
   python scripts/publish_skill.py <skill_dir> --no-push
   ```
5. Run the bundled validator to ensure the SKILL.md doesn't break:
   ```bash
   python ~/.workbuddy/plugins/cache/workbuddy-builtin/skill-skill-creator/0.1.0/scripts/package_skill.py . .
   ```
6. Open a PR.

## Style rules for SKILL.md

- Frontmatter `agent_created: true` until first upstream release.
- Imperative voice throughout.
- Workflow numbered 1..N.
- Every error class in the script must map to one recovery path in the SKILL.md.

## Releasing

Maintainers cut releases through the GitHub UI.

- Bump version in SKILL.md frontmatter if present.
- The zip in the repo root is the marketplace-installable artifact.
- Release notes follow `.github/RELEASE_TEMPLATE.md`.
