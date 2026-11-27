# F006 — GitHub Actions CI/CD Journal

## Decisions and implementation

- Kept CI and release in one `.github/workflows/ci.yml`, with a single test job and tag-gated release job as approved in F006 plan P016.
- Workflow permissions default to `contents: read`; only the release job receives `contents: write` (R002, P003).
- Used `astral-sh/setup-uv` and `uv python install` so the Python version comes from repository `.python-version`; locked dependencies are installed in CI before the existing test suite (R001, P001).
- Used `softprops/action-gh-release` to create the GitHub Release and attach `dist/*`; no PyPI publishing or application deployment is configured (R002, P002–P003).
- README release instructions require a new tag for each release and say not to move or overwrite tags (R003, P004).
- Hosted run 45925751747 failed during action resolution because `astral-sh/setup-uv@v10` is not a published ref. Updated both uses to the published `v10.4.0` tag; this is an implementation correction within P001/P002, not a scope change.
- Hosted run 45925790800 reached the suite but three retrieval tests failed because LlamaIndex lazily initialized its default OpenAI LLM without a key. Its existing test mode selects `MockLLM` when `IS_TESTING` is set. Added `IS_TESTING: "1"` only to the test job, preserving credential-free CI and using the library's existing mock behavior (R001, P005, P009).

## Verification evidence

### Implementation review

- Test source inspection: existing tests use monkeypatched/mock provider clients, temporary PDFs and local fixtures; no `.env`, API credentials, production PDF corpus or Chroma index is required by the test suite.
- `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/ci.yml")'`: passed (`YAML syntax parsed`). `actionlint` is not installed, so no actionlint validation was performed.
- Workflow review confirms `push` and `pull_request` triggers, Ubuntu runner, Python installation via `uv python install` (reads `.python-version`), locked sync/test commands, tag-ref guard, `needs: test`, `uv build`, `dist/*` release files and job-scoped contents write permission.

### Automated verification

- `uv sync --locked`: passed locally; 141 packages already satisfied from the lockfile.
- `env -u OPENAI_API_KEY -u COHERE_API_KEY IS_TESTING=1 uv run pytest -q`: passed locally; **35 passed**, 6 dependency deprecation warnings, 2.66 seconds. The provider keys were explicitly unset; tests used generated fixtures and temporary indexes, not the local corpus/index.
- `uv build`: passed locally; generated `dist/nse_rag-0.1.0.tar.gz` and `dist/nse_rag-0.1.0-py3-none-any.whl`.
- `git diff --check`: passed for tracked changes. Final staged check remains before commit.

### Hosted verification

- GitHub-hosted CI run 45925751747: failed before tests because the `setup-uv@v10` action ref did not resolve. Corrected to `setup-uv@v10.4.0`.
- GitHub-hosted CI run 45925790800: dependency install passed; 32 tests passed and three retrieval tests failed because LlamaIndex attempted default OpenAI LLM initialization. Added its existing `IS_TESTING` mock switch to the test job; credential-free local rerun and subsequent hosted run pass.
- GitHub-hosted CI run [45925897742](https://github.com/suriyadeepan/nse-rag/actions/runs/45925897742): **passed** on Ubuntu with the locked dependency install and test suite. The test job took 29 seconds. The release job was skipped because this was a branch push, as expected.
- Version-tagged release and asset inspection: pending as tracked by T005; requires merge to the intended release branch and a new `v*` tag. No release tag has been created as part of implementation.

## Convergence

- **Status: NOT CONVERGED.**
- **Finding F001 — Severity: Medium, external verification pending.** Lineage: R002/A004–A006 → P002–P003/P014 → T005. Affected files: `.github/workflows/ci.yml`, `README.md`. Evidence: hosted CI run 45925897742 passed; `uv build` generated the wheel and source archive locally; workflow condition and permissions were reviewed. No actual tag run or Release asset listing exists. The README requires merge then a new tag; creating a release from this feature branch would not follow that procedure. Remaining work: after merge, create a new release tag and inspect the release assets under T005.
