#!/usr/bin/env python3
"""Verify that a patch level is built only from php/php-src code.

For each branch of versions.json built from a repository other than php/php-src:
- the base commit must have the tree of the official release tag (README.md aside, and the
  files of base_exceptions in versions.json, for a branch based on its "-dev" version bump);
- every commit between the base and the pinned commit must come from php/php-src.
  Its official counterpart is found through the "cherry picked from commit" trailer,
  or else by author and subject, and the two patches are compared with git patch-id.

Official counterparts are looked up on the official branches of the same version
(PHP-x.y and the PHP-x.y-* fix branches) first, then on the supported branches.
GitHub serves every commit of the fork network under php/php-src, backport branches'
included, so a counterpart must be on a branch or tag of a clone of php/php-src. A
trailer that names a commit of another backport branch is followed through that commit's
own trailers.

A commit passes when it is identical to its official counterpart; when it differs, or
has no counterpart, only in files that do not go into the binaries (NEWS, tests,
README.md, .github); or when it adds and removes the same lines as its counterpart, in
hunks of the same functions, so that only the surrounding context differs (the older
branch's code around the change). Any other commit must be reviewed in
verification/reviews.json.
Writes verification/<branch>.md and exits 1 when a commit is not reviewed.

Usage: verify_backports.py [branch ...]   (default: every branch of versions.json)
"""

import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

OFFICIAL = 'php/php-src'
TOKEN = os.environ.get('GITHUB_TOKEN', '')
BASE_EXCEPTIONS = {'README.md'}
CHERRY_PICK = re.compile(r'cherry picked from commit ([0-9a-f]{40})')
ADVISORY = re.compile(r'GHSA(?:-[0-9a-z]{4}){3}|CVE-\d{4}-\d{4,}')


def request(path, accept='application/vnd.github+json'):
    headers = {'Accept': accept, 'X-GitHub-Api-Version': '2022-11-28'}
    if TOKEN:
        headers['Authorization'] = 'Bearer ' + TOKEN
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://api.github.com' + path, headers=headers)) as r:
                text = r.read().decode('utf-8', 'replace')
                return json.loads(text) if accept.endswith('json') else text
        except urllib.error.HTTPError as error:
            if error.code in (404, 422):
                return None
            if error.code in (403, 429) and attempt < 5:  # rate limits, the search API's in particular
                time.sleep(15 * (attempt + 1))
                continue
            raise


def tree(repo, commit):
    sha = request(f'/repos/{repo}/commits/{commit}')['commit']['tree']['sha']
    data = request(f'/repos/{repo}/git/trees/{sha}?recursive=1')
    if data['truncated']:
        sys.exit(f'{repo}@{commit}: tree listing truncated')
    return {item['path']: item['sha'] for item in data['tree'] if item['type'] == 'blob'}


def patch(repo, sha):
    return request(f'/repos/{repo}/commits/{sha}', 'application/vnd.github.patch')


def official_commits():
    """Commits of the branches and tags of php/php-src, from a clone without trees (about
    50 MB) kept in the temporary directory and fetched again at each run."""
    path = os.path.join(tempfile.gettempdir(), 'php-src-official.git')
    if os.path.isdir(path):
        subprocess.run(['git', '-C', path, 'fetch', '--quiet', '--prune', 'origin',
                        '+refs/heads/*:refs/heads/*', '+refs/tags/*:refs/tags/*'], check=True)
    else:
        subprocess.run(['git', 'clone', '--quiet', '--bare', '--filter=tree:0',
                        f'https://github.com/{OFFICIAL}.git', path], check=True)
    out = subprocess.run(['git', '-C', path, 'rev-list', '--all'], capture_output=True, text=True, check=True)
    return set(out.stdout.split())


def official_sha(sha, official):
    """Full id of a commit of php/php-src, None for a commit of a fork."""
    if sha in official:
        return sha
    matches = [s for s in official if s.startswith(sha)] if len(sha) < 40 else []
    return matches[0] if len(matches) == 1 else None


def patch_id(text):
    out = subprocess.run(['git', 'patch-id', '--stable'], input=text.encode('utf-8'), capture_output=True, check=True)
    return out.stdout.split()[0].decode() if out.stdout else None


def files(text):
    """Patch content per file, without index lines and hunk line numbers."""
    result, current = {}, None
    for line in text.splitlines():
        match = re.match(r'diff --git a/(\S+) b/', line)
        if match:
            current = match.group(1)
            result[current] = []
        elif current and not line.startswith('index '):
            result[current].append(re.sub(r'^@@ -\d+(,\d+)? \+\d+(,\d+)? @@', '@@', line))
    if result:  # format-patch signature at the end of the last file
        last = result[current]
        while last and (last[-1] in ('--', '') or re.fullmatch(r'\d+(\.\d+)+.*', last[-1])):
            last.pop()
    return result


def changed_lines(lines):
    """Added and removed lines of a file's patch, whitespace-normalised, as sorted lists."""
    def pick(sign):
        return sorted(' '.join(l[1:].split()) for l in lines if l.startswith(sign) and not l.startswith(sign * 3))
    return pick('+'), pick('-')


def hunk_functions(lines):
    """Function names git gives in the hunk headers of a file's patch."""
    return [l for l in lines if l.startswith('@@')]


def same_changes(mine, theirs):
    """True when, in every file that goes into the binaries, the backport adds and removes the
    same lines as the official patch, in hunks of the same functions: only the context differs."""
    paths = {p for p in set(mine) | set(theirs) if not outside_binaries(p)}
    return all(p in mine and p in theirs and changed_lines(mine[p]) == changed_lines(theirs[p])
               and hunk_functions(mine[p]) == hunk_functions(theirs[p]) for p in paths)


def adaptation_summary(mine, theirs):
    """What an adapted backport changed compared with the official patch, in files that go into the binaries."""
    notes = []
    dropped = sorted(p for p in theirs if p not in mine and not outside_binaries(p))
    extra = sorted(p for p in mine if p not in theirs and not outside_binaries(p))
    common = [p for p in mine if p in theirs and not outside_binaries(p)]
    same = [p for p in common if changed_lines(mine[p]) == changed_lines(theirs[p])]
    added_same = [p for p in common if p not in same and changed_lines(mine[p])[0] == changed_lines(theirs[p])[0]]
    other = [p for p in common if p not in same and p not in added_same]
    if same:
        notes.append(f'{len(same)} file(s) with the same added and removed lines (context differs)')
    if added_same:
        notes.append(f'same added lines, different removed lines in {", ".join(added_same)}')
    if other:
        notes.append(f'different changes in {", ".join(other)}')
    if dropped:
        notes.append(f'official changes not applied to {", ".join(dropped)}')
    if extra:
        notes.append(f'backport-only changes to {", ".join(extra)}')
    return '; '.join(notes)


def outside_binaries(path):
    """Files that are not compiled into, nor shipped with, the binary zips."""
    return (path in ('NEWS', 'README.md') or path.startswith(('.github/', 'tests/'))
            or '/tests/' in path or path.endswith('.phpt'))


def official_branch_commits(minor, tag):
    """Subject -> commits of the official PHP-x.y and PHP-x.y-* branches since the release tag."""
    index = {}
    refs = request(f'/repos/{OFFICIAL}/git/matching-refs/heads/PHP-{minor}') or []
    for ref in refs:
        branch = ref['ref'].removeprefix('refs/heads/')
        if branch != f'PHP-{minor}' and not branch.startswith(f'PHP-{minor}-'):
            continue  # PHP-8.1.34 and the like are release branches
        for commit in (request(f'/repos/{OFFICIAL}/compare/{tag}...{branch}') or {'commits': []})['commits']:
            index.setdefault(commit['commit']['message'].splitlines()[0], []).append(commit['sha'])
    return index


def official_counterpart(repo, commit, own_patch_id, code, branch_index, official, known=None):
    """php/php-src commit this one was taken from, preferring one with the same patch id.
    code: the commit changes files that go into the binaries.
    known: the official commit recorded by a review, for backports that do not name it."""
    message = commit['commit']['message']
    pending = [known] if known else []
    pending += branch_index.get(message.splitlines()[0], [])
    pending += CHERRY_PICK.findall(message)
    candidates, followed = [], set()
    while pending:
        sha = pending.pop(0)
        full = official_sha(sha, official)
        if full:
            candidates += [full] if full not in candidates else []
        elif sha not in followed and len(followed) < 10:
            # Cherry-picked from another backport branch: follow that commit's trailers
            followed.add(sha)
            picked = request(f'/repos/{repo}/commits/{sha}')
            pending += CHERRY_PICK.findall(picked['commit']['message']) if picked else []
    # Same author and subject, for a commit that names none, or for a code commit whose
    # trailers stop at another backport (a bare "NEWS" subject would match unrelated commits)
    if not candidates and (not followed or code):
        subject = message.splitlines()[0].replace('"', ' ')
        query = urllib.parse.quote(f'repo:{OFFICIAL} author-name:"{commit["commit"]["author"]["name"]}" "{subject}"')
        found = request(f'/search/commits?q={query}&per_page=20') or {'items': []}
        candidates = [item['sha'] for item in found['items'] if item['sha'] in official
                      and item['commit']['message'].splitlines()[0] == message.splitlines()[0]]
    best = None
    for sha in candidates:
        text = patch(OFFICIAL, sha)
        if text is None:
            continue
        if patch_id(text) == own_patch_id:
            return sha, text
        best = best or (sha, text)
    return best or (None, None)


def verify(minor, config, reviews, official):
    repo, head, base = config['php_src_repo'], config['php_src_sha'], config['base_commit']
    tag = config['base_tag']
    base_files, tag_files = tree(repo, base), tree(OFFICIAL, tag)
    base_diff = sorted(p for p in set(base_files) | set(tag_files) if base_files.get(p) != tag_files.get(p))
    base_ok = set(base_diff) <= BASE_EXCEPTIONS | set(config.get('base_exceptions', []))

    comparison = request(f'/repos/{repo}/compare/{base}...{head}')
    if comparison['status'] != 'ahead' or comparison['total_commits'] != len(comparison['commits']):
        sys.exit(f'{minor}: {head} is not a plain descendant of {base} (or more than 250 commits)')

    branch_index = official_branch_commits(minor, tag)
    rows, details, counts, unreviewed = [], [], {}, []
    for number, commit in enumerate(comparison['commits'], 1):
        sha = commit['sha']
        own = patch(repo, sha)
        own_id = patch_id(own)
        mine = files(own)
        code = not all(outside_binaries(p) for p in mine)
        counterpart, official_text = official_counterpart(repo, commit, own_id, code, branch_index, official,
                                                          reviews.get(sha, {}).get('official'))
        if counterpart is None:
            if not code:
                result = 'no official commit, NEWS/tests only'
            else:
                result = 'no official commit'
                details.append((number, sha, commit['commit']['message'].splitlines()[0], None,
                                [line for path in mine for line in [f'+++ backport/{path}', *mine[path]]]))
        elif patch_id(official_text) == own_id:
            result = 'identical'
        else:
            theirs = files(official_text)
            differing = sorted(p for p in set(mine) | set(theirs) if mine.get(p) != theirs.get(p))
            if all(outside_binaries(p) for p in differing):
                result = 'identical code, NEWS/tests differ'
            elif same_changes(mine, theirs):
                result = 'same changes, context differs'
            else:
                result = 'adapted'
                diff = [f'# {adaptation_summary(mine, theirs)}']
                for path in differing:
                    if not outside_binaries(path):
                        diff += difflib.unified_diff(theirs.get(path, []), mine.get(path, []),
                                                     f'official/{path}', f'backport/{path}', n=1, lineterm='')
                details.append((number, sha, commit['commit']['message'].splitlines()[0], counterpart, diff))
        counts[result] = counts.get(result, 0) + 1
        review = reviews.get(sha, {}).get('note', '')
        if result in ('adapted', 'no official commit') and not review:
            unreviewed.append(sha)
        # Advisory ids from the backport's message and from the official commit's
        official_message = official_text.split('\n---\n', 1)[0] if official_text else ''
        advisories = sorted(set(ADVISORY.findall(commit['commit']['message'] + official_message)))
        rows.append(f"| {number} | [{sha[:7]}](https://github.com/{repo}/commit/{sha}) "
                    f"| {f'[{counterpart[:7]}](https://github.com/{OFFICIAL}/commit/{counterpart})' if counterpart else '-'} "
                    f"| {commit['commit']['message'].splitlines()[0].replace('|', chr(92) + '|')} "
                    f"| {', '.join(advisories) or '-'} | {result} | {review or ('**to review**' if sha in unreviewed else '')} |")
        print(f'{minor} {number:3}/{len(comparison["commits"])} {sha[:7]} {result}', flush=True)

    summary = ', '.join(f'{n} {result}' for result, n in sorted(counts.items()))
    lines = [f'# PHP {minor}: verification of {repo}@{head[:7]}', '',
             f'Generated by `.github/scripts/verify_backports.py`. Branch `{config["php_src_branch"]}`, '
             f'pinned at [{head[:7]}](https://github.com/{repo}/commit/{head}), compared with {OFFICIAL}.', '',
             f'Base: [{base[:7]}](https://github.com/{repo}/commit/{base}) has the tree of the official tag '
             f'[{tag}](https://github.com/{OFFICIAL}/releases/tag/{tag})'
             + (f', apart from {", ".join(base_diff)}.' if base_diff else '.') if base_ok
             else f'Base: **{base[:7]} differs from {tag}**: {", ".join(base_diff)}', '',
             f'{len(rows)} commits: {summary}.', '',
             '| # | Commit | Official commit | Subject | Advisories | Result | Review |',
             '|---|---|---|---|---|---|---|', *rows]
    if details:
        lines += ['', '## Commits to review', '',
                  'Adapted commits: differences between the official patch and the backport in files that go '
                  'into the binaries (hunk line numbers ignored). Commits without an official counterpart: '
                  'their whole patch.']
        for number, sha, subject, _, diff in details:
            lines += ['', f'<details><summary>#{number} {sha[:7]} {subject}</summary>', '', '```diff', *diff, '```',
                      '', '</details>']
    os.makedirs('verification', exist_ok=True)
    with open(f'verification/{minor}.md', 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    return base_ok, unreviewed


def main():
    with open('versions.json', encoding='utf-8') as f:
        versions = json.load(f)
    reviews_path = 'verification/reviews.json'
    reviews = json.load(open(reviews_path, encoding='utf-8')) if os.path.exists(reviews_path) else {}
    official = official_commits()
    failed = False
    for minor in sys.argv[1:] or list(versions):
        config = versions[minor]
        if config['php_src_repo'] == OFFICIAL:
            print(f'{minor}: built from {OFFICIAL}, nothing to verify')
            continue
        base_ok, unreviewed = verify(minor, config, reviews, official)
        if not base_ok:
            print(f'{minor}: base commit differs from {config["base_tag"]}')
        if unreviewed:
            print(f'{minor}: {len(unreviewed)} commit(s) to review: {" ".join(s[:7] for s in unreviewed)}')
        failed = failed or not base_ok or bool(unreviewed)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
