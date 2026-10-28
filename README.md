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
- Which zip: Thread Safe (`php-<version>-Win32-…`) for Apache with mod_php, as only it
  contains the Apache module; NTS (`php-<version>-nts-Win32-…`) for IIS, nginx or the
  command line. Take x64 or x86 to match your server. The devel packs are only for
  building extensions. From patch level 3, releases no longer carry the debug and test
  packs, which almost nobody downloaded.

Current patch levels. Each one carries the php-src security fixes published since the
end of life of the branch, as backported by Remi Collet and listed in
[PATCHES.md](PATCHES.md). Binaries are attached to the
[releases](https://github.com/Jamalofski/php-eol-security/releases).

| Branch | Version | Toolchain |
|---|---|---|
| 8.1 | **PHP 8.1.34 Patch Level 2** (`8.1.34-pl2`) | `vs16` (MSVC v142, Visual C++ 2019) |
| 8.0 | **PHP 8.0.30 Patch Level 2** (`8.0.30-pl2`) | `vs16` (MSVC v142, Visual C++ 2019) |
| 7.4 | **PHP 7.4.33 Patch Level 2** (`7.4.33-pl2`) | `vc15` (MSVC v141, Visual C++ 2017) |

Patch level 1 carried only the fix for CVE-2026-109618 and CVE-2026-109619 that the PHP
team published for these branches.

## How it is built

| | |
|---|---|
| Sources | the last official release of the branch plus the official php-src security fixes published since, as backported by Remi Collet in [remicollet/php-src-security](https://github.com/remicollet/php-src-security) and checked commit by commit against php-src (see below); pinned per branch in [versions.json](versions.json). The only change made here is the version string |
| Build Provider | `Jamal TANTAOUI (unofficial EOL security build) - https://github.com/Jamalofski/php-eol-security` (8.0 and later; PHP 7.4 has no such entry) |
| Toolchain | the one of the official builds of the branch (table above), on `windows-2022` |
| Build scripts | the official [php/php-windows-builder](https://github.com/php/php-windows-builder) (pinned commit): same configure flags and PGO as the official releases of the branch; for PHP 7, the workflow adds back OCI8 and PDO_OCI, which the PHP 7 releases shipped and the builder no longer enables |
| Oracle SDK | OCI8 and PDO_OCI are built against the current Oracle Instant Client SDK, as the official builder does |
| Dependencies | official packages from downloads.php.net for the branch. The package series of 7.3 and 7.2 stopped in 2020-2021 (OpenSSL 1.1.1l and 1.1.1g, curl 7.70.0 and 7.67.0, zlib 1.2.11): their builds take the newer vc15 packages of 7.4 for OpenSSL (1.1.1s, the last vc15 build published), curl, nghttp2, libssh2, libxml2 and zlib (`deps_overrides` in [versions.json](versions.json)), and the build checks the versions the binaries load |
| SBOM | each binary zip comes with its CycloneDX SBOM (`.cdx.json`), produced by the official builder (from patch level 2; patch level 2 also had an SPDX copy) |
| Variants | x64 / x86, TS / NTS |

ABI and CRT are those of the official builds of the branch: existing extension
DLLs load as before.

Everything is in [`.github/workflows/build.yml`](.github/workflows/build.yml). Each
release links the run that produced it; GitHub keeps run logs for 90 days.

## Verification of the sources

Before every build, [`verify_backports.py`](.github/scripts/verify_backports.py) checks
that the pinned sources are the official release plus official php-src commits, and the
build stops otherwise:

- the base commit must have the tree of the official release tag;
- every later commit is compared, with `git patch-id`, to the php/php-src commit it was
  taken from (its "cherry picked from commit" line, or the same author and subject);
- a commit passes when it is identical to it; when it differs only in files that are not
  part of the binaries (NEWS, tests); or when it adds and removes the same lines in the
  same functions, the older code around the change being the only difference;
- any other commit, adapted to the older branch or without an official counterpart, needs
  a review recorded in [`verification/reviews.json`](verification/reviews.json).

The reports in [`verification/`](verification/) list every commit with its official
counterpart and result, and show what each reviewed commit changes.

## Verify

```
php -v                                # PHP 8.1.34-pl2 ...
php -i | findstr "Build Provider"     # Jamal TANTAOUI (unofficial EOL security build) ... (8.0+)
```

Check the zips against `SHA256SUMS` attached to the release. Each zip also has a
signed build provenance attestation, which ties it to the workflow run and the
commit that built it:

```
gh attestation verify php-8.1.34-pl2-nts-Win32-vs16-x64.zip --repo Jamalofski/php-eol-security
```

## Upstream watch

Every Monday, [`watch-upstream.yml`](.github/workflows/watch-upstream.yml) opens an
issue labelled `upstream-watch` when:

- the backport branch a patch level is built from gets new commits;
- the official `PHP-x.y` branch, or an official `PHP-x.y-*` fix branch, gets new commits,
  or a new fix branch appears;
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
