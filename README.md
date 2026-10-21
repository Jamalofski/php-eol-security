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

Patch levels, each fixing CVE-2026-109618 and CVE-2026-109619. Binaries are
attached to the [releases](https://github.com/Jamalofski/php-eol-security/releases).

| Branch | Version | Toolchain |
|---|---|---|
| 8.1 | **PHP 8.1.34 Patch Level 1** (`8.1.34-pl1`) | `vs16` (MSVC v142, Visual C++ 2019) |
| 8.0 | **PHP 8.0.30 Patch Level 1** (`8.0.30-pl1`) | `vs16` (MSVC v142, Visual C++ 2019) |
| 7.4 | **PHP 7.4.33 Patch Level 1** (`7.4.33-pl1`) | `vc15` (MSVC v141, Visual C++ 2017) |

## How it is built

| | |
|---|---|
| Sources | the last official release of the branch plus the fixes listed in [PATCHES.md](PATCHES.md), pinned per branch in [versions.json](versions.json); the only change made here is the version string |
| Build Provider | `Jamal TANTAOUI (unofficial EOL security build) - https://github.com/Jamalofski/php-eol-security` (8.0 and later; PHP 7.4 has no such entry) |
| Toolchain | the one of the official builds of the branch (table above), on `windows-2022` |
| Build scripts | the official [php/php-windows-builder](https://github.com/php/php-windows-builder) (pinned commit): same configure flags and PGO as the official releases of the branch; for 7.4, the workflow adds back OCI8 and PDO_OCI, which the 7.4 releases shipped and the builder no longer enables |
| Oracle SDK | OCI8 and PDO_OCI are built against the current Oracle Instant Client SDK, as the official builder does |
| Dependencies | official packages from downloads.php.net for the branch |
| Variants | x64 / x86, TS / NTS |

ABI and CRT are those of the official builds of the branch: existing extension
DLLs load as before.

Everything is in [`.github/workflows/build.yml`](.github/workflows/build.yml). Each
release links the run that produced it; GitHub keeps run logs for 90 days.

## Verify

```
php -v                                # PHP 8.1.34-pl1 ...
php -i | findstr "Build Provider"     # Jamal TANTAOUI (unofficial EOL security build) ... (8.0+)
```

Check the zips against `SHA256SUMS` attached to the release. Each zip also has a
signed build provenance attestation, which ties it to the workflow run and the
commit that built it:

```
gh attestation verify php-8.1.34-pl1-nts-Win32-vs16-x64.zip --repo Jamalofski/php-eol-security
```

## Upstream watch

Every Monday, [`watch-upstream.yml`](.github/workflows/watch-upstream.yml) checks
php-src and opens an issue labelled `upstream-watch` when:

- the branch a patch level is built from, or its base branch `PHP-x.y`, gets new commits;
- a new `PHP-x.y-*` fix branch appears for a branch built here;
- php-src publishes new security advisories.

## Limits

- Only the fixes listed in [PATCHES.md](PATCHES.md). Bundled libraries stay at the
  versions of the branch (OpenSSL 1.1.1, itself end-of-life, among others).
- Migrating to a supported PHP version remains the real fix.
- Provided as is, without warranty.

## License

This product includes PHP software, freely available from
<http://www.php.net/software/>. PHP is distributed under the PHP License,
version 3.01. Each zip ships it as `license.txt`, with the licenses of the code PHP
bundles in `readme-redist-bins.txt`, as the official zips do.
