import unittest
from datetime import date
import xml.etree.ElementTree as ET
from unittest.mock import patch
from scripts import update_languages as app
from scripts import profile_charts as charts


class ProfileChartsTest(unittest.TestCase):
    def test_calendar_fills_missing_days_and_excludes_dates_outside_window(self):
        days = charts.calendar_days({'2026-10-14': 3, '2026-10-12': 1,
                                     '2024-01-01': 9, '2026-10-15': 8}, date(2026, 10, 14))
        self.assertEqual(len(days), 365)
        self.assertEqual(days[-3:], [('2026-10-12', 1), ('2026-10-13', 0), ('2026-10-14', 3)])
        self.assertEqual(sum(value for _, value in days), 4)

    def test_dashboard_has_one_block_per_day_and_real_language_proportions(self):
        days = [('2026-10-12', 0), ('2026-10-13', 2), ('2026-10-14', 5)]
        root = ET.fromstring(charts.render_dashboard('GitHub', [('Python', 75), ('Java', 25)],
                                                     2, days, '2026-10-14', 'bytes'))
        ns = {'s': 'http://www.w3.org/2000/svg'}
        blocks = root.findall('.//s:g[@class="day"]', ns)
        self.assertEqual([b.attrib['data-count'] for b in blocks], ['0', '2', '5'])
        self.assertEqual(len(root.findall('.//s:circle[@class="language-slice"]', ns)), 2)
        text = ' '.join(root.itertext())
        self.assertIn('75.0%', text)
        self.assertIn('25.0%', text)
        self.assertIn('7 contribuições', text)

    def test_empty_dashboard_has_no_fake_language_slices(self):
        root = ET.fromstring(charts.render_dashboard('GitLab', [], 0, [('2026-10-14', 0)],
                                                     '2026-10-14', 'média'))
        self.assertIn('Sem linguagens detectadas', ' '.join(root.itertext()))
        self.assertEqual(root.findall('.//{*}circle[@class="language-slice"]'), [])

    def test_github_graphql_errors_are_not_treated_as_empty_calendar(self):
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test-token'}), \
             patch.object(app, 'fetch_json', return_value={'errors': [{'message': 'denied'}]}):
            with self.assertRaises(RuntimeError):
                app.collect_github_calendar('person')

    def test_calendar_failure_preserves_existing_cards(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / 'github-languages.svg').write_text('previous')
            with patch.object(app, 'collect_github', return_value=({'Python': 100}, 1)), \
                 patch.object(app, 'collect_gitlab', return_value=({}, 0)), \
                 patch.object(app, 'collect_github_calendar', side_effect=RuntimeError('API unavailable')):
                with self.assertRaises(RuntimeError):
                    app.update(target, 'person', 'person')
            self.assertEqual((target / 'github-languages.svg').read_text(), 'previous')
