# Patches

Security fixes included in each patch level, on top of the last official release
of the branch. Each level includes everything from the previous ones.

Status: **upstream** = fix published by the PHP team for this branch;
**backport** = fix from a supported branch applied as is; **adapted** = backport
that needed changes (the commit message explains them); **n/a** = the branch is
not affected (the reason is given).

## PHP 8.1

Base: [php-8.1.34](https://github.com/php/php-src/releases/tag/php-8.1.34) (2025-12-16), last official 8.1 release.

### PHP 8.1.34 Patch Level 1 (8.1.34-pl1)

Source: [php/php-src@1d7dec1](https://github.com/php/php-src/commit/1d7dec178a094e6e75b229ce22754045f8c6070a)
(branch [`PHP-8.1-CVE-2026-109618-109619`](https://github.com/php/php-src/tree/PHP-8.1-CVE-2026-109618-109619))

| Advisory | CVE | Severity | Summary | Status | Commit |
|---|---|---|---|---|---|
| [GHSA-w8hw-w9fx-j79w](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) | CVE-2026-109618 | critical | RCE via OOM corruption | upstream | [1d7dec1](https://github.com/php/php-src/commit/1d7dec178a094e6e75b229ce22754045f8c6070a) |
| [GHSA-6wmf-4rv5-p3rp](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp) | CVE-2026-109619 | critical | RCE via stale global state | upstream | [1d7dec1](https://github.com/php/php-src/commit/1d7dec178a094e6e75b229ce22754045f8c6070a) |
