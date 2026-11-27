# F006 — GitHub Actions CI/CD Journal

## Decisions and implementation

- Kept CI and release in one `.github/workflows/ci.yml`, with a single test job and tag-gated release job as approved in F006 plan P016.
- Workflow permissions default to `contents: read`; only the release job receives `contents: write` (R002, P003).
- Used `astral-sh/setup-uv` and `uv python install` so the Python version comes from repository `.python-version`; locked dependencies are installed in CI before the existing test suite (R001, P001).
- Used `softprops/action-gh-release` to create the GitHub Release and attach `dist/*`; no PyPI publishing or application deployment is configured (R002, P002–P003).
- README release instructions require a new tag for each release and say not to move or overwrite tags (R003, P004).

## Verification evidence

### Implementation review

- Test source inspection: existing tests use monkeypatched/mock provider clients, temporary PDFs and local fixtures; no `.env`, API credentials, production PDF corpus or Chroma index is required by the test suite.
- `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/ci.yml")'`: passed (`YAML syntax parsed`). `actionlint` is not installed, so no actionlint validation was performed.
- Workflow review confirms `push` and `pull_request` triggers, Ubuntu runner, Python installation via `uv python install` (reads `.python-version`), locked sync/test commands, tag-ref guard, `needs: test`, `uv build`, `dist/*` release files and job-scoped contents write permission.

### Automated verification

- `uv sync --locked`: passed locally; 141 packages already satisfied from the lockfile.
- `uv run pytest -q`: passed locally; **35 passed**, 6 dependency deprecation warnings, 2.39 seconds. No API credentials or local corpus/index were configured.
- `uv build`: passed locally; generated `dist/nse_rag-0.1.0.tar.gz` and `dist/nse_rag-0.1.0-py3-none-any.whl`.
- `git diff --check`: passed for tracked changes. Final staged check remains before commit.

### Hosted verification

- GitHub-hosted CI run: pending; feature branch push is required.
- Version-tagged release and asset inspection: pending; requires a new `v*` tag after CI succeeds. No release tag has been created as part of implementation.
