"""Display GitHub's repository unique-visitor metric without a tracking pixel."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
from urllib.parse import quote
try:
    from .update_languages import fetch_json
except ImportError:
    from update_languages import fetch_json


def update(output, owner, repo):
    token = os.getenv('PROFILE_TRAFFIC_TOKEN') or os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('A token with access to repository traffic is required')
    data = fetch_json(f'https://api.github.com/repos/{quote(owner, safe="")}/{quote(repo, safe="")}/traffic/views', token)
    value = data.get('uniques')
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError('GitHub returned invalid unique visitor data')
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="30" viewBox="0 0 390 30" role="img" aria-labelledby="title desc">
<title id="title">Visitantes únicos do repositório · 14 dias: {value}</title>
<desc id="desc">Métrica oficial de tráfego do repositório GitHub. Atualizado: {stamp}. Abrir este SVG não incrementa o contador.</desc>
<rect x=".5" y=".5" width="389" height="29" rx="7" fill="#191226" stroke="#56406d"/>
<g font-family="DejaVu Sans, sans-serif" font-size="11"><text x="12" y="19" fill="#d8c9eb">Visitantes únicos do repositório · 14 dias</text>
<text x="375" y="20" fill="#f9a8d4" font-size="15" font-weight="700" text-anchor="end">{value}</text></g></svg>
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding='utf-8')
    print(f'GitHub repository traffic: {value} unique visitors in the last 14 days')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', default='V1nic1us')
    parser.add_argument('--repo', default='V1nic1us')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'assets' / 'visitors.svg')
    args = parser.parse_args()
    update(args.output, args.owner, args.repo)
