"""HTTP service that answers old site URLs with redirects to their new homes."""

import logging
import re
import time

import tornado.ioloop
import tornado.web

from link_redirector import __version__
from link_redirector.config import Settings, load_settings
from link_redirector.rules import FIXED_REDIRECTS, describe

log = logging.getLogger("link_redirector")


class HealthHandler(tornado.web.RequestHandler):
    """Liveness probe for the load balancer."""

    def initialize(self, started_at: float) -> None:
        self.started_at = started_at

    def get(self) -> None:
        self.write(
            {
                "status": "ok",
                "version": __version__,
                "uptime_seconds": int(time.monotonic() - self.started_at),
            }
        )


class RulesHandler(tornado.web.RequestHandler):
    """Lists the active redirect rules as JSON, for operators."""

    def initialize(self, rules: list[dict]) -> None:
        self.rules = rules

    def get(self) -> None:
        self.set_header("Cache-Control", "no-store")
        self.write({"count": len(self.rules), "rules": self.rules})


def build_handlers(settings: Settings) -> list[tuple]:
    """Assemble the route table: service endpoints first, then redirects."""
    fixed = {**FIXED_REDIRECTS, **settings.extra_redirects}
    handlers: list[tuple] = [
        (r"/health", HealthHandler, {"started_at": time.monotonic()}),
        (r"/rules", RulesHandler, {"rules": describe(fixed)}),
    ]
    for source, target in sorted(fixed.items()):
        handlers.append(
            (
                re.escape(source) + "/?",
                tornado.web.RedirectHandler,
                {"url": target},
            )
        )

    # The /legacy/ prefix was dropped in the restructure; the rest of the
    # path is unchanged, so /legacy/docs/setup now lives at /docs/setup.
    handlers.append((r"/legacy/(.*)", tornado.web.RedirectHandler, {"url": "/{0}"}))
    return handlers


def _log_request(handler: tornado.web.RequestHandler) -> None:
    request = handler.request
    log.info(
        "%d %s %s %.1fms",
        handler.get_status(),
        request.method,
        request.uri,
        1000.0 * request.request_time(),
    )


def make_app(settings: Settings | None = None) -> tornado.web.Application:
    """Create the Tornado application."""
    settings = settings or load_settings()
    return tornado.web.Application(
        build_handlers(settings),
        debug=settings.debug,
        log_function=_log_request,
    )


def main() -> None:
    """Serve the application until interrupted."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    settings = load_settings()
    app = make_app(settings)
    app.listen(settings.port, address=settings.address, xheaders=True)
    log.info("link-redirector %s listening on %s:%d", __version__, settings.address, settings.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
