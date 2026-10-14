"""Standalone SVG dashboards: isometric activity, languages and weekly rhythm."""
from datetime import date, timedelta
from html import escape
import math

COLORS = ['#c084fc', '#f472b6', '#818cf8', '#67e8f9', '#fbbf24', '#86efac', '#94a3b8']


def calendar_days(values, end=None):
    end = end or date.today()
    start = end - timedelta(days=364)
    days = []
    for offset in range(365):
        day = (start + timedelta(days=offset)).isoformat()
        count = values.get(day, 0)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError('Invalid contribution count')
        days.append((day, count))
    return days


def render_dashboard(platform, languages, repo_count, days, updated, metric):
    """Render real calendar counts; language values are percentages totaling 100."""
    def text(x, y, value, size=16, color='#e2e8f0', extra=''):
        return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" {extra}>{escape(str(value))}</text>'

    def polygon(points, fill, extra=''):
        coords = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
        return f'<polygon points="{coords}" fill="{fill}" {extra}/>'

    total = sum(count for _, count in days)
    active = sum(count > 0 for _, count in days)
    maximum = max((count for _, count in days), default=0)
    label = f'{platform}: {total} contribuições em {len(days)} dias; {repo_count} repositórios com linguagens.'
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="850" viewBox="0 0 1280 850" role="img" aria-labelledby="title desc">',
             f'<title id="title">{escape(platform)} · atividade e linguagens de V1nic1us</title>',
             f'<desc id="desc">{escape(label)} Blocos proporcionais à atividade diária. {escape(metric)}.</desc>',
             '<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#111324"/><stop offset="1" stop-color="#191226"/></linearGradient></defs>',
             '<rect x="1" y="1" width="1278" height="848" rx="24" fill="url(#bg)" stroke="#352943"/>',
             '<g font-family="DejaVu Sans, Segoe UI, sans-serif">',
             text(42, 43, f'V1nic1us / {platform.upper()}', 14, '#c4b5fd', 'letter-spacing="3"'),
             text(42, 82, 'Um ano construindo, um dia de cada vez.', 26, '#f8fafc', 'font-weight="700"'),
             text(42, 110, 'ATIVIDADE EM 3D  /  ÚLTIMOS 365 DIAS', 12, '#a59bb5', 'letter-spacing="2"')]
    start_day = date.fromisoformat(days[0][0]) if days else date.today()
    offset = (start_day.weekday() + 1) % 7  # Sunday-first calendar
    for index, (day, count) in enumerate(days):
        week, weekday = divmod(index + offset, 7)
        x, y = 160 + week * 17 - weekday * 17, 185 + week * 8 + weekday * 8
        height = 3 + (math.sqrt(count / maximum) * 100 if maximum else 0)
        level = min(3, int(count / maximum * 3)) if maximum and count else 0
        top = ['#77608e', '#a78bfa', '#d28bea', '#f472b6'][level] if count else '#30263e'
        left = ['#4c3a61', '#7458b0', '#9c59b4', '#b34585'][level] if count else '#221b2d'
        right = ['#5e4877', '#8967cb', '#b572cd', '#d45a9c'][level] if count else '#292033'
        parts.append(f'<g class="day" data-date="{day}" data-count="{count}"><title>{day}: {count} contribuições</title>')
        parts.append(polygon([(x-7,y-height+3.5),(x,y-height+7),(x,y+7),(x-7,y+3.5)], left))
        parts.append(polygon([(x,y-height+7),(x+7,y-height+3.5),(x+7,y+3.5),(x,y+7)], right))
        parts.append(polygon([(x,y-height),(x+7,y-height+3.5),(x,y-height+7),(x-7,y-height+3.5)], top))
        parts.append('</g>')
    # Independent weekly rhythm: sums of contributions for each weekday.
    cx, cy, radius = 1060, 242, 90
    weekday_counts = [0] * 7
    for day, count in days:
        weekday_counts[date.fromisoformat(day).weekday()] += count
    def radial(index, scale):
        angle = -math.pi / 2 + index * 2 * math.pi / 7
        return cx + math.cos(angle) * radius * scale, cy + math.sin(angle) * radius * scale
    parts.append(text(cx, 126, 'RITMO DA SEMANA', 12, '#c4b5fd', 'text-anchor="middle" letter-spacing="2"'))
    for scale in (.25, .5, .75, 1):
        parts.append(polygon([radial(i, scale) for i in range(7)], 'none', 'stroke="#544065" stroke-dasharray="4 5"'))
    for i, name in enumerate(['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']):
        x, y = radial(i, 1.22)
        parts.append(text(round(x,2), round(y+4,2), name, 12, '#bcb0cb', 'text-anchor="middle"'))
    peak = max(weekday_counts) or 1
    parts.append(polygon([radial(i, value / peak) for i, value in enumerate(weekday_counts)], '#f472b6', 'fill-opacity="0.35" stroke="#f9a8d4" stroke-width="2"'))
    # A real donut: percentages of code, independent of contribution counts.
    parts.extend([text(44, 516, 'LINGUAGENS MAIS USADAS', 12, '#c4b5fd', 'letter-spacing="2"'),
                  '<circle cx="157" cy="648" r="86" fill="none" stroke="#30263e" stroke-width="35"/>'])
    running = 0
    circumference = 2 * math.pi * 86
    for index, (name, value) in enumerate(languages):
        length = value / 100 * circumference
        parts.append(f'<circle class="language-slice" cx="157" cy="648" r="86" fill="none" stroke="{COLORS[index % len(COLORS)]}" stroke-width="35" stroke-dasharray="{length:.4f} {circumference:.4f}" stroke-dashoffset="{-running:.4f}" transform="rotate(-90 157 648)"><title>{escape(name)}: {value:.1f}%</title></circle>')
        running += length
        y = 553 + index * 29
        parts.extend([f'<rect x="291" y="{y-10}" width="10" height="10" rx="3" fill="{COLORS[index % len(COLORS)]}"/>',
                      text(313, y, name, 14), text(570, y, f'{value:.1f}%', 14, '#c4b5fd', 'text-anchor="end"')])
    parts.append(text(157, 646, repo_count, 32, '#f8fafc', 'text-anchor="middle" font-weight="700"'))
    parts.append(text(157, 669, 'repositórios', 11, '#a59bb5', 'text-anchor="middle"'))
    if not languages:
        parts.append(text(291, 638, 'Sem linguagens detectadas', 17, '#d4c8df'))
        parts.append(text(291, 664, 'nos projetos públicos atuais.', 13, '#a59bb5'))
    parts.extend([text(44, 786, metric, 12, '#a59bb5'),
                  text(1240, 736, f'{total:,} contribuições'.replace(',', '.'), 30, '#f9a8d4', 'text-anchor="end" font-weight="700"'),
                  text(1240, 766, f'{active} dias ativos · pico de {maximum} em um dia', 15, '#bcb0cb', 'text-anchor="end"'),
                  text(44, 817, f'{days[0][0]} → {days[-1][0]}' if days else '', 11, '#8e819e'),
                  text(1240, 817, f'Atualizado: {updated} UTC', 11, '#8e819e', 'text-anchor="end"'), '</g></svg>'])
    return '\n'.join(parts) + '\n'
