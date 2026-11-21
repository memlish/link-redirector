"""Proof for CVE-2026-126347 / GHSA-5cjw-f85j-cv6r in link-redirector.

The /legacy/(.*) route redirects to "/{0}", so the captured path starts the
Location. Tornado 6.6.0 lets a path with extra leading slashes through, and a
browser reads "///host/..." as a link to another host. Fails on 6.6.0,
passes on 6.6.1. Harmless: it only talks to a local test server.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tornado.testing import AsyncHTTPTestCase  # noqa: E402

from link_redirector.app import make_app  # noqa: E402
from link_redirector.config import Settings  # noqa: E402


class LegacyRedirectStaysOnSiteTest(AsyncHTTPTestCase):
    def get_app(self):
        return make_app(Settings())

    def test_legacy_redirect_does_not_leave_site(self):
        response = self.fetch("/legacy///other-site.example/x", follow_redirects=False)
        location = response.headers.get("Location", "")
        self.assertFalse(
            location.startswith("//"),
            f"got {response.code} with off-site Location {location!r}",
        )
