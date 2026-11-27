# F006 — GitHub Actions CI/CD Plan

## Scope and implementation

- **P001** Add one `.github/workflows/ci.yml` with `push` and `pull_request` triggers, a single Ubuntu CI job, checkout, `uv` setup using `.python-version`, locked sync and `uv run pytest -q`. [R001, A001–A003]
- **P002** In the same workflow define one release job conditional on a pushed `v*` tag and dependent on CI; build with `uv build`, then create a GitHub Release with `dist/*` attached. [R002, A004–A005]
- **P003** Set workflow default permissions to read-only contents and grant contents write only to the release job. Do not add publishing or deployment steps. [R002, A006]
- **P004** Add the requested tag release instructions and immutable-new-tag guidance to `README.md`. [R003, A007]
- **P005** During implementation/convergence, inspect tests for external service credentials or local corpus/index assumptions; resolve only failures that prevent this stated CI job from working, recording any scope-relevant decision in this plan and evidence in the journal. [R001, A002–A003]

## Affected files and dependencies

- **P006** Add `.github/workflows/ci.yml`; update `README.md`; add F006 TODO and implementation journal under `docs/`; update local `.current`. [R001–R003]
- **P007** Reuse repository `.python-version`, `uv.lock`, project `dev` dependencies, pytest suite and `uv build`; use GitHub-hosted Ubuntu and `GITHUB_TOKEN`. No Python dependency changes are planned. [R001–R002]

## Architecture compatibility matrix

| Area | Status | Evidence / verification |
|---|---|---|
| Python runtime | VERIFIED for repository declaration; UNKNOWN on hosted runner | `.python-version` is `3.14`; `pyproject.toml` and `uv.lock` require Python >=3.14. Hosted installation remains to be exercised. |
| CPU architecture | ASSUMED | Plan targets GitHub-hosted `ubuntu-latest` x86_64; no hosted run evidence exists yet. |
| Native dependencies | ASSUMED for hosted Linux | Locked dependencies include ChromaDB/ONNX Runtime and PyMuPDF; `uv.lock` includes Linux x86_64 wheels for key native packages, but end-to-end install/test is unverified on GitHub. |
| Container format | UNKNOWN / not applicable | No container build or runtime is in scope. |
| Deployment target | VERIFIED as not applicable | Product is a local CLI; release creates downloadable Python build files only and performs no application deployment. |

Automated compatibility checks: hosted Ubuntu workflow runs `uv sync --locked` and the full `uv run pytest -q` suite. Tag release path additionally runs `uv build`; workflow permissions and conditions are reviewed from the workflow definition. Real-world verification requires a successful GitHub Actions run and inspection of the created release assets.

## Risks and mitigations

- **P008** Python 3.14 or native package wheels may fail on the hosted image. Use the repository version and lockfile as requested; rely on the actual hosted CI run as compatibility evidence. [R001, A002]
- **P009** The test suite may import optional credentials or rely on local corpus/index paths. Inspect its existing mocks and fixtures and adjust only necessary tests/setup if such a dependency is found; never inject API credentials. [R001, A003]
- **P010** A tag job could run without successful CI or receive excess write permissions. Make release depend on CI, guard by the `v*` ref, default workflow permissions to contents read, and scope contents write to release job. [R002, A004, A006]
- **P011** Tag and package version may differ because automated version updates are out of scope. The release instructions will require a new tag each time; release remains based on the tagged commit. [R003, O006]

## Acceptance and validation

- **P012** Review triggers, job dependency/condition, commands, runner, Python version source and permission scopes against R001–R002 and A001–A006.
- **P013** Confirm README steps and example tag match the workflow and prohibit moving/overwriting tags. [R003, A007]
- **P014** Run local checks only when implementing (workflow syntax/content review, existing test suite and package build as appropriate); record exact commands/outcomes. Then verify GitHub-hosted CI and an actual tag release before claiming real-world acceptance. [A001–A007]
- **P015** Keep implementation, automated test and hosted GitHub verification evidence distinct in the journal; no PyPI publication or deployment. [R002, O001–O007]

## Architecture decisions

- **P016** Keep CI and release in one workflow with one test job and one tag-only release job, matching the implementation principle. [R001–R002]
- **P017** Use a GitHub Release action with the job-scoped built-in token for asset upload; no separate credentials or publication registry. [R002]
