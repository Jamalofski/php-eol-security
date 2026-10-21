# PHP 8.1.34-cve2026 — unofficial Windows builds

PHP 8.1 is end-of-life. The PHP team published a minimal mitigation for
**CVE-2026-109618** ([GHSA-w8hw-w9fx-j79w](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w))
and **CVE-2026-109619** ([GHSA-6wmf-4rv5-p3rp](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp))
on the branch [`PHP-8.1-CVE-2026-109618-109619`](https://github.com/php/php-src/tree/PHP-8.1-CVE-2026-109618-109619),
but no 8.1 release or Windows binaries. This repository builds them.

**These are not official PHP Group binaries.**

## What is built

| | |
|---|---|
| Source | [php/php-src@1d7dec1](https://github.com/php/php-src/commit/1d7dec178a094e6e75b229ce22754045f8c6070a) — PHP 8.1.34 + the fix, nothing else |
| Version string | `8.1.34-cve2026` (only change to the sources) |
| Build Provider | `Jamal TANTAOUI (unofficial build, php-src@1d7dec1) - https://github.com/Jamalofski/php-8.1-cve-builds` |
| Toolchain | `vs16` (MSVC v142, Visual C++ 2019) on `windows-2022`, same as the official 8.1 builds |
| Build scripts | the official [php/php-windows-builder](https://github.com/php/php-windows-builder) (pinned commit), same configure flags and PGO as official builds |
| Dependencies | official `8.1-vs16` packages from downloads.php.net |
| Variants | x64 / x86, TS / NTS |

ABI and CRT are those of the official 8.1.34 vs16 builds: existing extension DLLs
built for 8.1 vs16 load as before.

Everything is in [`.github/workflows/build.yml`](.github/workflows/build.yml); each
release links the run that produced it, with its full logs.

## Verify

```
php -v                                # PHP 8.1.34-cve2026 ...
php -i | findstr "Build Provider"     # Jamal TANTAOUI (unofficial build, ...)
```

Check the zips against `SHA256SUMS` attached to the release.

## Limits

- Fixes only these two CVEs. Bundled libraries stay at their 8.1 versions
  (OpenSSL 1.1.1, itself end-of-life, among others).
- Migrating to a supported PHP version (8.3+) remains the real fix.
- Provided as is, without warranty. PHP is distributed under the PHP License.
