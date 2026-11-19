# php-eol-security

Unofficial Windows builds of end-of-life PHP (7.4, 8.0, 8.1), built from Remi Collet's
backport branches (remicollet/php-src-security) with the official php-windows-builder.
Every commit of those branches is verified against php/php-src before each build.

## Git, CI and delivery

- Trunk-based: commit on `main`, no pull request unless asked. A session branch is deleted
  once merged.
- A go on a change means commit, merge on `main` and push, in one step. Without a go:
  commit, then ask for the go in one question.
- A release is a separate, explicit go: run the Build workflow with `release=true`.
- Builds run only through `workflow_dispatch`; nothing runs on push.

## A new patch level

1. The weekly watch (`watch-upstream.yml`) opens an `upstream-watch` issue when Remi's
   branches, the official `PHP-x.y` branches or the php-src advisories move.
2. Pin the new commits in `versions.json` (`php_src_sha`, `patch_level`, `upstream_refs`).
3. Run `GITHUB_TOKEN=$(gh auth token) python .github/scripts/verify_backports.py <branch>`
   locally. Review every commit it reports and record the review in
   `verification/reviews.json`; rerun until it passes, and commit the reports.
4. Update `PATCHES.md` (fixes from the NEWS of the branch, with their commits) and the table
   of `README.md`.
5. Run a validation build (`release=false`), then the release on Jamal's go. Check each
   release: assets against `SHA256SUMS`, one attestation per zip, one CycloneDX SBOM per
   binary zip, no debug or test pack.

Published binaries must keep their provenance attestations, checksums, SBOM and immutable
releases; actions stay pinned by commit SHA.
