import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import update_languages as app


class LanguagesTest(unittest.TestCase):
    def test_github_pagination_excludes_forks_and_private_repos(self):
        def fetch(url, token=None):
            if 'page=1&' in url:
                return [{'fork': False, 'private': False, 'languages_url': 'languages/one'}] * 100
            if 'page=2&' in url:
                return [
                    {'fork': True, 'private': False, 'languages_url': 'excluded'},
                    {'fork': False, 'private': True, 'languages_url': 'private'},
                    {'fork': False, 'private': False, 'languages_url': 'languages/two'},
                ]
            return {'languages/one': {'Python': 3, 'Java': 1},
                    'languages/two': {'Java': 100}}[url]
        with patch.object(app, 'fetch_json', side_effect=fetch):
            totals, count = app.collect_github('person')
        self.assertEqual(totals, {'Python': 300, 'Java': 200})
        self.assertEqual(count, 101)

    def test_gitlab_averages_only_original_public_nonempty_projects(self):
        def fetch(url, token=None):
            if '/users?' in url:
                return [{'id': 7}]
            if '/users/7/projects?' in url:
                return [{'id': 1, 'visibility': 'public'},
                        {'id': 2, 'visibility': 'public'},
                        {'id': 3, 'visibility': 'public'},
                        {'id': 4, 'visibility': 'public', 'forked_from_project': {'id': 1}},
                        {'id': 5, 'visibility': 'private'}]
            if not url.endswith('/languages'):
                return {'id': int(url.split('/')[-1]), 'visibility': 'public'}
            return {1: {'Python': 100}, 2: {'Python': 50, 'Java': 50}, 3: {}}[int(url.split('/')[-2])]
        with patch.object(app, 'fetch_json', side_effect=fetch):
            totals, count = app.collect_gitlab('person')
        self.assertEqual(app.percentages(totals), [('Python', 75.0), ('Java', 25.0)])
        self.assertEqual(count, 2)

    def test_gitlab_checks_details_when_list_omits_fork_metadata(self):
        def fetch(url, token=None):
            if '/users?' in url:
                return [{'id': 7}]
            if '/users/7/projects?' in url:
                return [{'id': 8, 'visibility': 'public'}]
            if url.endswith('/projects/8'):
                return {'id': 8, 'visibility': 'public',
                        'forked_from_project': {'id': 2}}
            return {'Python': 100}
        with patch.object(app, 'fetch_json', side_effect=fetch):
            self.assertEqual(app.collect_gitlab('person'), ({}, 0))

    def test_svg_handles_empty_data_and_escapes_language_names(self):
        import xml.etree.ElementTree as ET
        for totals in ({}, {'A&B<script>': 2, 'Python': 1}):
            svg = app.render_card('GitHub', totals, 1, '2026-10-14', 'bytes')
            ET.fromstring(svg)
            self.assertNotIn('<script>', svg)

    def test_failure_keeps_previous_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / 'github-languages.svg').write_text('previous')
            with patch.object(app, 'collect_github', return_value=({'Python': 100}, 1)), \
                 patch.object(app, 'collect_gitlab', side_effect=RuntimeError('API unavailable')):
                with self.assertRaises(RuntimeError):
                    app.update(target, 'person', 'person')
            self.assertEqual((target / 'github-languages.svg').read_text(), 'previous')


if __name__ == '__main__':
    unittest.main()
