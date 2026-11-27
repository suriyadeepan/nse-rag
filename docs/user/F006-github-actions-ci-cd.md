# F006 — GitHub Actions CI/CD

## Objective

Add the smallest reliable GitHub Actions workflow to automatically test the project and create a downloadable package release. Prioritize a quick implementation with a high likelihood of success.

## Scope

- **CI:** Run the existing automated test suite on every push and pull request.
- **CD:** Build the Python package and attach the build artifacts to a GitHub Release when a `v*` version tag is pushed.
- Use GitHub-hosted runners and the existing `uv` environment.
- No application deployment is required for this local CLI project

## Requirements

### R001 — Continuous integration

Create `.github/workflows/ci.yml`:

- Trigger on `push` and `pull_request`.
- Check out the repository.
- Set up `uv` and install the Python version from the repository's `.python-version`.
- Install locked dependencies using `uv sync --locked`.
- Run the existing test suite using `uv run pytest -q`.
- Fail the workflow if dependency installation or any test fails.
- Do not require API credentials or call OpenAI/Cohere during CI; tests must use the existing mocks/local fixtures.

### R002 — Package release

- Run the release job only when a tag matching `v*` is pushed.
- Make the release job depend on successful CI.
- Build the package using `uv build`.
- Create a GitHub Release and attach the files from `dist/`.
- Grant write access to repository contents only to the release job; keep CI read-only.
- Do not publish to PyPI or deploy the application.

### R003 — Release instructions

Document the minimal release procedure in the README:

1. Merge the tested changes into the intended release branch (normally `main`).
2. Create and push a version tag, for example:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. Confirm the GitHub Actions workflow succeeds and the GitHub Release contains the built package files.

Use a new version tag for each release; do not move or overwrite an existing release tag.

## Acceptance criteria

- A push or pull request triggers the CI workflow.
- CI installs the locked dependencies and runs `uv run pytest -q` successfully on GitHub-hosted Linux.
- CI succeeds without `.env`, API keys, the local PDF corpus or the local Chroma index.
- Pushing a new `v*` tag triggers the release job only after CI succeeds.
- The GitHub Release contains the artifacts produced by `uv build`.
- Workflow permissions are limited as described above.
- README instructions match the implemented workflow.

## Out of scope

- Deploying an API, web app, CLI service or infrastructure.
- Docker/container publishing.
- PyPI publishing.
- Full-corpus ingestion, embedding or live OpenAI/Cohere calls in CI.
- Scheduled workflows, coverage services, matrix builds, caching optimizations or complex test stages.
- Automated version bumping, changelog generation or release branching.
- Production-grade supply-chain/security automation.

## Implementation principle

Use one workflow file, one test job and one tag-triggered release job. Reuse the existing test suite and package build. Avoid adding tools or workflow complexity unless the basic pipeline fails.
