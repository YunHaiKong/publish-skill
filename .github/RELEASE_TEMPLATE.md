## What's changed in publish_skill.py

- Bug fixes:
- New flags:
- Breaking changes (flag renames or removed flags):
- Documentation updates in SKILL.md / references:

## Validation

- [ ] `python publish_skill.py --help` runs cleanly
- [ ] Smoke test: `python publish_skill.py <some_skill_dir> --no-push` succeeds
- [ ] Validates a real skill end-to-end (full push path tested locally)

## Bundled skill-publisher.zip

- [ ] Re-zipped by running `package_skill.py` against the bundled SKILL.md
- [ ] Users who already have the publisher installed should re-import the new zip

## Breaking changes for downstream

- [ ] None
- [ ] Flag X renamed to Y (callers must update)
