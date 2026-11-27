# F006 — GitHub Actions CI/CD TODO

Canonical task and status source for F006. Mark tasks complete only after their acceptance evidence is recorded in the F006 journal.

## T001 — Implement CI workflow

- **Status:** COMPLETE — hosted CI run 45925897742 passed with locked sync and the full suite without provider keys.
- **Action:** Add the push and pull request CI job with checkout, `uv` setup from `.python-version`, `uv sync --locked`, and `uv run pytest -q`. Ensure it uses no API credentials or local corpus/index.
- **Files:** `.github/workflows/ci.yml`, `docs/006-github-actions-ci-cd.md`
- **Requirements / plan:** R001, A001–A003; P001, P005, P007–P009, P012
- **Acceptance:** CI job runs on GitHub-hosted Linux, executes the required commands, and contains no API credential configuration or corpus/index setup. Existing suite passes in the prescribed environment. Record command output and test evidence in the journal.
- **Dependencies:** None.

## T002 — Implement tag release job and scoped permissions

- **Status:** IMPLEMENTED — job conditions, permissions and build/upload steps are configured; real tag-triggered release verification remains in T005.
- **Action:** Add a release job to the same workflow, conditional on pushed `v*` tags and dependent on CI. Build with `uv build` and attach `dist/*` to a GitHub Release. Configure workflow default contents read and release-job contents write only.
- **Files:** `.github/workflows/ci.yml`, `docs/006-github-actions-ci-cd.md`
- **Requirements / plan:** R002, A004–A006; P002–P003, P007, P010–P012, P014–P017
- **Acceptance:** Workflow conditions ensure release runs only for matching pushed tags after CI succeeds; package build artifacts are the release assets; no PyPI or deployment step exists; write permission appears only on release job. Record local build and workflow inspection evidence.
- **Dependencies:** T001.

## T003 — Document release procedure

- **Status:** COMPLETE — README release steps match the workflow configuration.
- **Action:** Add the minimal README release procedure, including merge to intended branch, tag/push example, successful workflow/release asset confirmation, and new-tag-only guidance.
- **Files:** `README.md`, `docs/006-github-actions-ci-cd.md`
- **Requirements / plan:** R003, A007; P004, P011, P013
- **Acceptance:** README commands and instructions match workflow triggers and asset handling and explicitly prohibit moving/overwriting a prior release tag. Record documentation review evidence.
- **Dependencies:** T002.

## T004 — Validate, document evidence and converge

- **Status:** COMPLETE — requirements, plan lineage, local checks, hosted CI, permissions and README have been reviewed; tagged release verification is tracked separately in T005.
- **Action:** Review workflow syntax, requirements/plan/TODO lineage, permissions, README instructions and package output; run the test suite and package build in `uv`; record implementation, automated test and hosted verification separately. Inspect CI and release on GitHub when a workflow run and new version tag are available. Update task status only after evidence.
- **Files:** `.github/workflows/ci.yml`, `README.md`, `docs/006-github-actions-ci-cd.md`, `docs/006-github-actions-ci-cd-todo.md`
- **Requirements / plan:** R001–R003, A001–A007; P012–P017
- **Acceptance:** Local checks pass and are recorded with exact commands; hosted CI and release evidence are recorded if available. Unavailable real-world verification remains explicitly outstanding and is not represented as passed. `git diff --check` passes. Feature converges against all requirements and acceptance criteria or records remaining external verification.
- **Dependencies:** T001–T003.

## T005 — Verify a version-tagged GitHub Release

- **Status:** NOT STARTED — requires merge to the intended release branch and selection of a new release tag.
- **Action:** After the feature is merged and CI passes on the intended release commit, use a new `v*` tag following the README procedure. Verify the release job runs after CI and the GitHub Release contains both files from `uv build`. Do not move or overwrite an existing tag.
- **Files:** `.github/workflows/ci.yml`, `README.md`, `docs/006-github-actions-ci-cd.md`, `docs/006-github-actions-ci-cd-todo.md`
- **Requirements / plan:** R002, A004–A006; P002–P003, P014–P017
- **Acceptance:** A GitHub-hosted tag run succeeds and its Release page contains the source distribution and wheel produced by `uv build`; record the run URL and asset names in the journal.
- **Dependencies:** T001–T004 and merge to the intended release branch.

## Lineage coverage

- R001 → P001, P005, P007–P009, P012 → T001, T004 → hosted CI configuration and suite evidence.
- R002 → P002–P003, P007, P010, P012, P014, P016–P017 → T002, T004 → tag condition, dependency, package assets and job permission review.
- R003 → P004, P011, P013 → T003, T004 → README release procedure review.
- A001–A007 → P001–P004, P012–P015 → T001–T004 → workflow, tests, package build, README and hosted verification evidence.
- A004–A006 → P002–P003, P014, P017 → T005 → real tag run and release asset inspection (pending a future release tag).
