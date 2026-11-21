# link-redirector

Keeps old links working after the website was restructured. The front proxy
sends retired paths here, and this service answers each one with a permanent
(301) redirect to the page's new address.

## Rules

- **Fixed redirects** map one old page to its new home, for example
  `/old-pricing` to `/pricing`. They live in `src/link_redirector/rules.py`.
- **Prefix moves**: the `/legacy/` section was folded into the main site, so
  `/legacy/<path>` now redirects to `/<path>`.
- Query strings are carried over to the new address.

`GET /rules` lists the active rules as JSON. `GET /health` is the liveness probe.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `LINK_REDIRECTOR_ADDRESS` | `127.0.0.1` | Address to listen on |
| `LINK_REDIRECTOR_PORT` | `8080` | Port to listen on |
| `LINK_REDIRECTOR_DEBUG` | `false` | Tornado debug mode |
| `LINK_REDIRECTOR_EXTRA` | empty | Extra fixed redirects, `/from=/to,/from=/to` |

## Development

```
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q
PYTHONPATH=src .venv/bin/python -m link_redirector.app
```
