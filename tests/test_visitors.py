import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import update_visitors as app


class VisitorsTest(unittest.TestCase):
    def test_badge_uses_unique_visitors_not_page_hits(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'visitors.svg'
            with patch.dict('os.environ', {'PROFILE_TRAFFIC_TOKEN': 'test'}), \
                 patch.object(app, 'fetch_json', return_value={'count': 100, 'uniques': 7, 'views': []}):
                app.update(target, 'person', 'person')
            content = target.read_text()
            self.assertIn('>7</text>', content)
            self.assertNotIn('>100</text>', content)
            self.assertIn('14 dias', content)

    def test_invalid_traffic_preserves_previous_badge(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'visitors.svg'
            target.write_text('previous')
            with patch.dict('os.environ', {'PROFILE_TRAFFIC_TOKEN': 'test'}), \
                 patch.object(app, 'fetch_json', return_value={'count': 100}):
                with self.assertRaises(ValueError):
                    app.update(target, 'person', 'person')
            self.assertEqual(target.read_text(), 'previous')
