# publish-skill

One-shot publisher for WorkBuddy skills: validate → package → README → push to GitHub → print marketplace upload steps.

## What it does

A single command that takes a WorkBuddy skill directory and ships it end-to-end:

```
$ python publish_skill.py ~/.workbuddy/skills/my-skill
```

| Step | Action |
|---|---|
| 1 | Validate skill structure via `package_skill.py` |
| 2 | Generate distribution zip |
| 3 | Generate README.md (with SVG workflow) if missing |
| 4 | Check / create GitHub repo |
| 5 | Copy to temp workdir → commit → push to `main` |
| 6 | Print WorkBuddy marketplace manual upload instructions |

## Install

Just copy `publish_skill.py` somewhere on your `PATH` (or invoke by full path).

Requirements:
- Python 3.8+
- GitHub CLI (`gh`) installed and authenticated (`gh auth login`)
- WorkBuddy `skill-creator` skill installed (provides `package_skill.py`)

## Usage

```
python publish_skill.py <skill_dir> [options]
```

### Required

- `skill_dir` — path to the skill source directory (must contain `SKILL.md`)

### Options

| Flag | Default | Description |
|---|---|---|
| `--repo NAME` | skill directory name | GitHub repo name |
| `--visibility public\|private` | public | Repo visibility |
| `--no-push` | — | Package only, skip GitHub push |
| `--message "msg"` | `Release {name}` | Commit message |
| `--user NAME` | read from `gh` | Git user name |
| `--email EMAIL` | `{user}@users.noreply.github.com` | Git email |

### Examples

```bash
# Full publish
python publish_skill.py ~/.workbuddy/skills/topic-idea-generator

# Smoke test (package only, no push)
python publish_skill.py ./my-skill --no-push

# Private repo
python publish_skill.py ./my-skill --visibility private

# Custom repo name
python publish_skill.py ./topic-idea-generator --repo my-cool-topic-tool
```

## Why it exists

Manually publishing a WorkBuddy skill today requires:

1. Run `package_skill.py` to validate
2. Write a rich README (often skipped because it's tedious)
3. Create GitHub repo via `gh repo create`
4. `git init` → `add` → `commit` → `push`
5. Re-upload zip to WorkBuddy marketplace via UI

`publish_skill.py` collapses all of that into one command, defaults pulled from your environment, and bakes in the SVG workflow template so the README doesn't look half-baked.

## How it reads your GitHub identity

It calls `gh api user --jq .login` to read the currently authenticated `gh` account, so you don't need to pass `--user` every time.

The commit author is set per-command via `git -c user.name=... -c user.email=...` to avoid touching your global git config.

## Output

After a successful run you'll see:

- A fresh zip in the skill's parent directory
- A pushed GitHub repo
- A printed block with the exact steps to upload the zip into the WorkBuddy marketplace UI

The marketplace has no public CLI upload path today, so the last step is intentionally a printed checklist rather than an automated action.

## Files

```
publish-skill/
├── README.md
└── publish_skill.py
```

## License

MIT
