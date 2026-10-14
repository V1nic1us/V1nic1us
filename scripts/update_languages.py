"""Generate public repository language cards with Python's standard library."""
import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
from html import escape
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

try:
    from .profile_charts import calendar_days, render_dashboard
except ImportError:
    from profile_charts import calendar_days, render_dashboard


def fetch_json(url, token=None, payload=None):
    headers = {'User-Agent': 'V1nic1us-profile', 'Accept': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(payload).encode() if payload is not None else None
    if body is not None:
        headers['Content-Type'] = 'application/json'
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=headers, data=body), timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f'API returned HTTP {error.code}: {url}') from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError(f'Could not reach API: {url}') from None
        time.sleep(2 ** (attempt + 1))


def pages(base_url, token=None):
    page = 1
    while True:
        separator = '&' if '?' in base_url else '?'
        items = fetch_json(f'{base_url}{separator}page={page}&per_page=100', token)
        if not isinstance(items, list):
            raise ValueError('Expected a repository list')
        yield from items
        if len(items) < 100:
            break
        page += 1


def collect_github(username):
    token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    totals, count = Counter(), 0
    url = f'https://api.github.com/users/{quote(username, safe="")}/repos?type=owner'
    for repo in pages(url, token):
        if repo.get('fork') or repo.get('private'):
            continue
        languages = fetch_json(repo['languages_url'], token)
        if languages:
            totals.update(languages)
            count += 1
    return dict(totals), count


def collect_gitlab(username):
    token = os.getenv('GITLAB_TOKEN')
    users = fetch_json('https://gitlab.com/api/v4/users?' + urlencode({'username': username}), token)
    if len(users) != 1:
        raise ValueError(f'GitLab user not found: {username}')
    totals, count = Counter(), 0
    url = f'https://gitlab.com/api/v4/users/{users[0]["id"]}/projects?owned=true&visibility=public'
    for repo in pages(url, token):
        if repo.get('forked_from_project') or repo.get('visibility') != 'public':
            continue
        detail = fetch_json(f'https://gitlab.com/api/v4/projects/{repo["id"]}', token)
        if detail.get('forked_from_project') or 'mr_default_target_self' in detail:
            continue
        languages = fetch_json(f'https://gitlab.com/api/v4/projects/{repo["id"]}/languages', token)
        if languages:
            totals.update(languages)
            count += 1
    return dict(totals), count


def percentages(totals):
    total = sum(totals.values())
    if not total:
        return []
    return [(name, value * 100 / total)
            for name, value in sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))]


def collect_github_calendar(username):
    token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('GITHUB_TOKEN is required to query the GitHub contribution calendar')
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=364)).replace(hour=0, minute=0, second=0, microsecond=0)
    query = """query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) { contributionsCollection(from: $from, to: $to) {
        contributionCalendar { weeks { contributionDays { date contributionCount } } }
      } }
    }"""
    response = fetch_json('https://api.github.com/graphql', token, {
        'query': query, 'variables': {'login': username, 'from': start.isoformat(), 'to': now.isoformat()}})
    if response.get('errors') or not response.get('data', {}).get('user'):
        raise RuntimeError('GitHub contribution calendar query failed')
    weeks = response['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    values = {day['date']: day['contributionCount'] for week in weeks for day in week['contributionDays']}
    return calendar_days(values, now.date())


def collect_gitlab_calendar(username):
    # This is the public profile calendar endpoint, not the versioned REST API.
    values = fetch_json(f'https://gitlab.com/users/{quote(username, safe="")}/calendar.json')
    if not isinstance(values, dict):
        raise ValueError('Invalid GitLab contribution calendar')
    return calendar_days(values, datetime.now(timezone.utc).date())


def render_card(platform, totals, count, date, metric, days=None):
    ranking = percentages(totals)
    rows = ranking[:6]
    if len(ranking) > 6:
        rows.append(('Outras', sum(value for _, value in ranking[6:])))
    return render_dashboard(platform, rows, count, days or calendar_days({}), date, metric)


def update(output, github_user, gitlab_user):
    # Complete both requests before replacing any existing results.
    github, gh_count = collect_github(github_user)
    gitlab, gl_count = collect_gitlab(gitlab_user)
    gh_days = collect_github_calendar(github_user)
    gl_days = collect_gitlab_calendar(gitlab_user)
    date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    output.mkdir(parents=True, exist_ok=True)
    for platform, totals, count, metric, days in [
        ('GitHub', github, gh_count, 'Linguagens: proporção por bytes de código', gh_days),
        ('GitLab', gitlab, gl_count, 'Linguagens: média dos percentuais por projeto', gl_days),
    ]:
        target = output / f'{platform.lower()}-languages.svg'
        target.write_text(render_card(platform, totals, count, date, metric, days), encoding='utf-8')
        print(f'{platform}: {count} repositories with languages; {len(totals)} languages')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--github-user', default='V1nic1us')
    parser.add_argument('--gitlab-user', default='V1nic1us')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'assets')
    args = parser.parse_args()
    update(args.output, args.github_user, args.gitlab_user)
