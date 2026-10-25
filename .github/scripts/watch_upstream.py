#!/usr/bin/env python3
"""Watch the sources of the patch levels for changes that may call for a new one.

Opens an issue in this repository, labelled "upstream-watch", for:
- commits on the branch a patch level is built from (php_src_repo/php_src_branch)
  after the pinned commit;
- commits on the official php-src branches of upstream_refs after the commit
  recorded there, or the removal of one of them;
- a new PHP-x.y-* branch on php-src, for a branch listed in versions.json;
- php-src security advisories published since WATCH_SINCE (one issue per batch).
A finding already reported by an issue, open or closed, is not reported again.
Set DRY_RUN=1 to print the issues instead of opening them.
"""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

UPSTREAM = 'php/php-src'
LABEL = 'upstream-watch'
REPO = os.environ.get('GITHUB_REPOSITORY', 'Jamalofski/php-eol-security')
TOKEN = os.environ.get('GITHUB_TOKEN', '')
WATCH_SINCE = os.environ['WATCH_SINCE']
NOTIFY = os.environ.get('NOTIFY', '')
DRY_RUN = os.environ.get('DRY_RUN') == '1'


def request(method, path, body=None):
    headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    if TOKEN:
        headers['Authorization'] = 'Bearer ' + TOKEN
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request('https://api.github.com' + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def reported_issues():
    issues, page = [], 1
    while True:
        batch = request('GET', f'/repos/{REPO}/issues?labels={LABEL}&state=all&per_page=100&page={page}')
        if not batch:
            return issues
        issues += batch
        page += 1


def commit_link(sha):
    return f'[{sha[:7]}](https://github.com/{UPSTREAM}/commit/{sha})'


def branch_link(branch):
    return f'[`{branch}`](https://github.com/{UPSTREAM}/tree/{branch})'


def new_commits(repo, branch, known, level, built_from):
    """Finding for commits on repo/branch after the known commit, or for the branch's removal."""
    comparison = request('GET', f'/repos/{repo}/compare/{known}...{branch}')
    if comparison is None and request('GET', f'/repos/{repo}/branches/{branch}') is None:
        return (f'Branch {branch} of {repo} was deleted',
                f'`{branch}` no longer exists on {repo} ({level} is built from {built_from}). '
                'Its commits may have moved to another branch: check them.')
    if comparison is None or comparison['behind_by'] > 0:
        return (f'History of {repo} {branch} was rewritten',
                f'`{branch}` on {repo} no longer contains {known[:7]}, the commit recorded for it '
                f'({level} is built from {built_from}). Check what changed before building anything from it.')
    if comparison['ahead_by'] == 0:
        return None
    commits = comparison['commits']
    lines = '\n'.join(f"- [{c['sha'][:7]}](https://github.com/{repo}/commit/{c['sha']}) "
                      f"{c['commit']['message'].splitlines()[0]}" for c in commits)
    return (f"New commits on {repo} {branch} (head {commits[-1]['sha'][:7]})",
            f"[`{branch}`](https://github.com/{repo}/tree/{branch}) has {comparison['ahead_by']} commit(s) "
            f'after {known[:7]} that {level} (built from {built_from}) does not include:\n\n{lines}\n\n'
            'If they fix security issues, build the next patch level: pin the new commits in versions.json, '
            'run .github/scripts/verify_backports.py, review the adapted commits, update PATCHES.md, '
            'then run the Build workflow.')


def branch_findings(minor, config):
    level = f"{config['base_version']}-pl{config['patch_level']}"
    repo, pinned = config['php_src_repo'], config['php_src_sha']
    built_from = f'{repo}@{pinned[:7]}'
    finding = new_commits(repo, config['php_src_branch'], pinned, level, built_from)
    if finding:
        yield finding
    # Official branches of this version, with the commit each one was at when last checked
    for branch, known in config.get('upstream_refs', {}).items():
        finding = new_commits(UPSTREAM, branch, known, level, built_from)
        if finding:
            yield finding


def new_branch_findings(minor, config):
    known = set(config.get('upstream_refs', {})) | {config['php_src_branch']}
    for ref in request('GET', f'/repos/{UPSTREAM}/git/matching-refs/heads/PHP-{minor}-') or []:
        branch = ref['ref'].removeprefix('refs/heads/')
        if branch in known:
            continue
        head = request('GET', f"/repos/{UPSTREAM}/commits/{ref['object']['sha']}")
        message = head['commit']['message'].splitlines()[0]
        yield (f'New branch on {UPSTREAM}: {branch}',
               f"{branch_link(branch)} appeared on {UPSTREAM}. Head: {commit_link(head['sha'])} {message} "
               f"({head['commit']['committer']['date'][:10]}).\n\n"
               f'It may carry security fixes for PHP {minor}, which is end-of-life: check it and, '
               'if so, build the next patch level.')


def advisory_finding(versions, reported_text):
    advisories = request('GET', f'/repos/{UPSTREAM}/security-advisories'
                                '?state=published&sort=published&direction=desc&per_page=100') or []
    new = sorted((a for a in advisories
                  if a['published_at'] >= WATCH_SINCE and a['ghsa_id'] not in reported_text),
                 key=lambda a: a['published_at'])
    if not new:
        return None
    rows = '\n'.join(
        f"| {a['published_at'][:10]} | [{a['ghsa_id']}]({a['html_url']}) | {a['cve_id'] or '-'} "
        f"| {a['severity']} | {a['summary'].replace('|', chr(92) + '|')} "
        f"| {' / '.join(v['vulnerable_version_range'] or '?' for v in a['vulnerabilities'] or []) or '?'} |"
        for a in new)
    branches = ', '.join(sorted(versions, key=lambda minor: [int(part) for part in minor.split('.')]))
    count = f"{len(new)} new php-src security advisor{'y' if len(new) == 1 else 'ies'}"
    return (f"{count} ({datetime.now(timezone.utc):%Y-%m-%d})",
            f'{count}:\n\n| Published | Advisory | CVE | Severity | Summary | Affected |\n'
            f'|---|---|---|---|---|---|\n{rows}\n\n'
            f'Check whether {branches} are affected and whether the PHP team published a fix for them; '
            'fixes go to the next patch level of each branch.')


def main():
    with open('versions.json', encoding='utf-8') as f:
        versions = json.load(f)
    issues = reported_issues()
    reported_titles = {issue['title'] for issue in issues}
    reported_text = '\n'.join(issue.get('body') or '' for issue in issues)

    findings = []
    for minor, config in versions.items():
        findings += branch_findings(minor, config)
        findings += new_branch_findings(minor, config)
    findings = [f for f in findings if f[0] not in reported_titles]
    advisories = advisory_finding(versions, reported_text)
    if advisories:
        findings.append(advisories)

    if findings and not DRY_RUN:
        try:
            request('POST', f'/repos/{REPO}/labels', {
                'name': LABEL, 'color': 'd93f0b',
                'description': 'Upstream php-src change that may call for a new patch level'})
        except urllib.error.HTTPError as error:
            if error.code != 422:  # already exists
                raise
    for title, body in findings:
        if NOTIFY:
            body += f'\n\ncc @{NOTIFY}'
        if DRY_RUN:
            print(f'--- {title}\n{body}\n')
        else:
            issue = request('POST', f'/repos/{REPO}/issues', {'title': title, 'body': body, 'labels': [LABEL]})
            print(f"Opened {issue['html_url']}: {title}")
    print(f'{len(findings)} new finding(s)')


if __name__ == '__main__':
    main()
