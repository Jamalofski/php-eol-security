# php-eol-security — unofficial security builds of end-of-life PHP

Once a PHP branch reaches end of life, the PHP team stops publishing releases and
Windows binaries for it, even when a fix exists. This repository builds Windows
binaries of end-of-life branches with the security fixes listed in
[PATCHES.md](PATCHES.md).

**These are not official PHP Group binaries.**

## Versions

`<last official release>-pl<N>`, for example `8.1.34-pl1`, `8.1.34-pl2`…

- `pl` (patch level) is understood by `version_compare()` and Composer:
  `8.1.34 < 8.1.34-pl1 < 8.1.34-pl2 < 8.1.35`.
- Each patch level includes the fixes of the previous ones.
- Release tags are `php-<version>`; zips keep the official naming
  (`php-8.1.34-pl1-Win32-vs16-x64.zip`, `php-8.1.34-pl1-nts-Win32-vs16-x64.zip`…).

Current: **8.1.34-pl1** — fixes CVE-2026-109618 and CVE-2026-109619.

## How it is built

| | |
|---|---|
| Sources | pinned php-src commit, see [PATCHES.md](PATCHES.md); only change made here is the version string |
| Build Provider | `Jamal TANTAOUI (unofficial EOL security build) - https://github.com/Jamalofski/php-eol-security` |
| Toolchain | 8.1: `vs16` (MSVC v142, Visual C++ 2019) on `windows-2022`, same as the official builds |
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
php -i | findstr "Build Provider"     # Jamal TANTAOUI (unofficial EOL security build) ...
```

Check the zips against `SHA256SUMS` attached to the release.

## Limits

- Only the fixes listed in [PATCHES.md](PATCHES.md). Bundled libraries stay at the
  versions of the branch (OpenSSL 1.1.1 for 8.1, itself end-of-life, among others).
- Migrating to a supported PHP version remains the real fix.
- Provided as is, without warranty. PHP is distributed under the PHP License.
