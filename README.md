# php-eol-security — unofficial security builds of end-of-life PHP

Once a PHP branch reaches end of life, the PHP team stops publishing releases and
Windows binaries for it, even when a fix exists. This repository builds Windows
binaries of end-of-life branches with the security fixes listed in
[PATCHES.md](PATCHES.md).

**These are not official PHP Group binaries.**

## Versions

`<last official release>-pl<N>`, for example `8.1.34-pl1`, `8.1.34-pl2`…,
named "PHP 8.1.34 Patch Level 1", "Patch Level 2"…

- `pl` (patch level) is understood by `version_compare()` and Composer:
  `8.1.34 < 8.1.34-pl1 < 8.1.34-pl2 < 8.1.35`.
- Each patch level includes the fixes of the previous ones.
- Release tags are `php-<version>`; zips keep the official naming
  (`php-8.1.34-pl1-Win32-vs16-x64.zip`, `php-8.1.34-pl1-nts-Win32-vs16-x64.zip`…).

Current, each fixing CVE-2026-109618 and CVE-2026-109619:

| Branch | Version | Toolchain |
|---|---|---|
| 8.1 | **PHP 8.1.34 Patch Level 1** (`8.1.34-pl1`) | `vs16` (MSVC v142, Visual C++ 2019) |
| 8.0 | **PHP 8.0.30 Patch Level 1** (`8.0.30-pl1`) | `vs16` (MSVC v142, Visual C++ 2019) |
| 7.4 | **PHP 7.4.33 Patch Level 1** (`7.4.33-pl1`) | `vc15` (MSVC v141, Visual C++ 2017) |

## How it is built

| | |
|---|---|
| Sources | pinned php-src commit per branch in [versions.json](versions.json), see [PATCHES.md](PATCHES.md); only change made here is the version string |
| Build Provider | `Jamal TANTAOUI (unofficial EOL security build) - https://github.com/Jamalofski/php-eol-security` (8.0 and later; PHP 7.4 has no such entry) |
| Toolchain | the one of the official builds of the branch (table above), on `windows-2022` |
| Build scripts | the official [php/php-windows-builder](https://github.com/php/php-windows-builder) (pinned commit): same configure flags and PGO as official builds |
| Dependencies | official packages from downloads.php.net for the branch |
| Variants | x64 / x86, TS / NTS |

ABI and CRT are those of the official builds of the branch: existing extension
DLLs load as before.

Everything is in [`.github/workflows/build.yml`](.github/workflows/build.yml); each
release links the run that produced it, with its full logs.

## Verify

```
php -v                                # PHP 8.1.34-pl1 ...
php -i | findstr "Build Provider"     # Jamal TANTAOUI (unofficial EOL security build) ... (8.0+)
```

Check the zips against `SHA256SUMS` attached to the release.

## Limits

- Only the fixes listed in [PATCHES.md](PATCHES.md). Bundled libraries stay at the
  versions of the branch (OpenSSL 1.1.1, itself end-of-life, among others).
- Migrating to a supported PHP version remains the real fix.
- Provided as is, without warranty. PHP is distributed under the PHP License.
