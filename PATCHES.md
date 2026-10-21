# Patches

Security fixes included in each patch level, on top of the last official release
of the branch. Each level includes everything from the previous ones. Each section
names the exact php-src commit built; [versions.json](versions.json) pins the
current level of each branch.

Status: **upstream** = fix published by the PHP team for this branch;
**backport** = fix from a supported branch applied as is; **adapted** = backport
that needed changes (the commit message explains them); **n/a** = the branch is
not affected (the reason is given).

## PHP 8.1

Base: [php-8.1.34](https://github.com/php/php-src/releases/tag/php-8.1.34) (2025-12-18), last official 8.1 release.
The fix sits on the `PHP-8.1` branch, whose sources are identical to the tag apart
from CI files under `.github/`.

### PHP 8.1.34 Patch Level 1 (8.1.34-pl1)

Source: [php/php-src@1d7dec1](https://github.com/php/php-src/commit/1d7dec178a094e6e75b229ce22754045f8c6070a)
(branch [`PHP-8.1-CVE-2026-109618-109619`](https://github.com/php/php-src/tree/PHP-8.1-CVE-2026-109618-109619))

| Advisory | CVE | Severity | Summary | Status | Commit |
|---|---|---|---|---|---|
| [GHSA-w8hw-w9fx-j79w](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) | CVE-2026-109618 | critical | RCE via OOM corruption | upstream | [1d7dec1](https://github.com/php/php-src/commit/1d7dec178a094e6e75b229ce22754045f8c6070a) |
| [GHSA-6wmf-4rv5-p3rp](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp) | CVE-2026-109619 | critical | RCE via stale global state | upstream | [1d7dec1](https://github.com/php/php-src/commit/1d7dec178a094e6e75b229ce22754045f8c6070a) |

## PHP 8.0

Base: [php-8.0.30](https://github.com/php/php-src/releases/tag/php-8.0.30) (2023-08-03), last official 8.0 release.
The fix sits on the `PHP-8.0` branch, whose sources are identical to the tag apart
from `NEWS`.

### PHP 8.0.30 Patch Level 1 (8.0.30-pl1)

Source: [php/php-src@82f8f31](https://github.com/php/php-src/commit/82f8f31b16a035c1b67cc253e79f7cc288f4cc20)
(branch [`PHP-8.0-CVE-2026-109618-109619`](https://github.com/php/php-src/tree/PHP-8.0-CVE-2026-109618-109619))

| Advisory | CVE | Severity | Summary | Status | Commit |
|---|---|---|---|---|---|
| [GHSA-w8hw-w9fx-j79w](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) | CVE-2026-109618 | critical | RCE via OOM corruption | upstream | [82f8f31](https://github.com/php/php-src/commit/82f8f31b16a035c1b67cc253e79f7cc288f4cc20) |
| [GHSA-6wmf-4rv5-p3rp](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp) | CVE-2026-109619 | critical | RCE via stale global state | upstream | [82f8f31](https://github.com/php/php-src/commit/82f8f31b16a035c1b67cc253e79f7cc288f4cc20) |

## PHP 7.4

Base: [php-7.4.33](https://github.com/php/php-src/releases/tag/php-7.4.33) (2022-11-03), last official 7.4 release.
The fix sits on the `PHP-7.4` branch, whose sources are identical to the tag apart
from `NEWS` and a `-dev` version bump, which the build replaces with `7.4.33-pl1`.

### PHP 7.4.33 Patch Level 1 (7.4.33-pl1)

Source: [php/php-src@712e60f](https://github.com/php/php-src/commit/712e60f9edfd03f0960fc4fc3c2c375f42b90aa2)
(branch [`PHP-7.4-CVE-2026-109618-109619`](https://github.com/php/php-src/tree/PHP-7.4-CVE-2026-109618-109619))

| Advisory | CVE | Severity | Summary | Status | Commit |
|---|---|---|---|---|---|
| [GHSA-w8hw-w9fx-j79w](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) | CVE-2026-109618 | critical | RCE via OOM corruption | upstream | [712e60f](https://github.com/php/php-src/commit/712e60f9edfd03f0960fc4fc3c2c375f42b90aa2) |
| [GHSA-6wmf-4rv5-p3rp](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp) | CVE-2026-109619 | critical | RCE via stale global state | upstream | [712e60f](https://github.com/php/php-src/commit/712e60f9edfd03f0960fc4fc3c2c375f42b90aa2) |
