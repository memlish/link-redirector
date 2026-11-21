import json

import pytest
from tornado.testing import AsyncHTTPTestCase

from link_redirector.app import make_app
from link_redirector.config import Settings, parse_extra_redirects


class RedirectorTest(AsyncHTTPTestCase):
    def get_app(self):
        return make_app(Settings(extra_redirects={"/careers-2024": "/careers"}))

    def test_health(self):
        response = self.fetch("/health")
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body)["status"], "ok")

    def test_rules_lists_fixed_and_prefix_rules(self):
        response = self.fetch("/rules")
        self.assertEqual(response.code, 200)
        body = json.loads(response.body)
        sources = {rule["from"] for rule in body["rules"]}
        self.assertIn("/old-pricing", sources)
        self.assertIn("/careers-2024", sources)
        self.assertIn("/legacy/*", sources)
        self.assertEqual(body["count"], len(body["rules"]))

    def test_fixed_redirect(self):
        response = self.fetch("/old-pricing", follow_redirects=False)
        self.assertEqual(response.code, 301)
        self.assertEqual(response.headers["Location"], "/pricing")

    def test_fixed_redirect_accepts_trailing_slash(self):
        response = self.fetch("/about-us/", follow_redirects=False)
        self.assertEqual(response.code, 301)
        self.assertEqual(response.headers["Location"], "/company")

    def test_extra_redirect_from_settings(self):
        response = self.fetch("/careers-2024", follow_redirects=False)
        self.assertEqual(response.code, 301)
        self.assertEqual(response.headers["Location"], "/careers")

    def test_legacy_prefix_is_dropped(self):
        response = self.fetch("/legacy/docs/setup", follow_redirects=False)
        self.assertEqual(response.code, 301)
        self.assertEqual(response.headers["Location"], "/docs/setup")

    def test_legacy_keeps_query_string(self):
        response = self.fetch("/legacy/blog?page=2", follow_redirects=False)
        self.assertEqual(response.code, 301)
        self.assertEqual(response.headers["Location"], "/blog?page=2")

    def test_unknown_path_is_404(self):
        response = self.fetch("/no-such-page", follow_redirects=False)
        self.assertEqual(response.code, 404)


def test_parse_extra_redirects():
    assert parse_extra_redirects(" /a=/b, ,/c=/d ") == {"/a": "/b", "/c": "/d"}
    with pytest.raises(ValueError):
        parse_extra_redirects("/a")
