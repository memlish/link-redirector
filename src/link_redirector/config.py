"""Settings, read from environment variables with development defaults."""

import os
from dataclasses import dataclass, field


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{name} must be an integer, got {value!r}") from None


def parse_extra_redirects(raw: str) -> dict[str, str]:
    """Parse "from=to,from=to" into a mapping.

    Lets ops add a one-off redirect without a release. Blank entries are
    skipped; both sides must be site paths starting with "/".
    """
    redirects: dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        source, sep, target = entry.partition("=")
        source, target = source.strip(), target.strip()
        if not sep or not source.startswith("/") or not target.startswith("/"):
            raise ValueError(f"bad redirect entry {entry!r}, expected /from=/to")
        redirects[source] = target
    return redirects


@dataclass(frozen=True)
class Settings:
    address: str = "127.0.0.1"
    port: int = 8080
    debug: bool = False
    extra_redirects: dict[str, str] = field(default_factory=dict)


def load_settings() -> Settings:
    """Build Settings from LINK_REDIRECTOR_* environment variables."""
    return Settings(
        address=os.environ.get("LINK_REDIRECTOR_ADDRESS", "127.0.0.1"),
        port=_env_int("LINK_REDIRECTOR_PORT", 8080),
        debug=_env_bool("LINK_REDIRECTOR_DEBUG", False),
        extra_redirects=parse_extra_redirects(
            os.environ.get("LINK_REDIRECTOR_EXTRA", "")
        ),
    )
