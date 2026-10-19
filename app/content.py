"""Mission content. One server can run several missions (sessions): every app/mission_<key>.py is one.

A request picks its mission by the first part of its URL (/s30/..., /working-with-lists/...; see main.py), and
`C.<NAME>` (C = this module) then reads that mission's module. Without a prefix, and in scripts and tests, the
mission is MISSION from the environment (default s29), so a single-mission deployment works as before.

Each mission module defines LEVELS, QUESTIONS, CONCEPTS, TYPE_LABEL, BADGES, STAGE_BADGE, TOTAL,
LEVEL_BY_ID, VISUAL_PRO (question type, badge id), UI (texts the pages show) and optionally SLUG (its URL name).
"""
import contextvars
import importlib
import os
from pathlib import Path

DEFAULT = os.environ.get("MISSION", "s29").strip().lower() or "s29"
_found = sorted(p.stem[len("mission_"):] for p in Path(__file__).parent.glob("mission_*.py"))
_only = [m.strip().lower() for m in os.environ.get("MISSIONS", "").split(",") if m.strip()]   # limit what this server offers
KEYS = [k for k in _found if (not _only or k in _only or k == DEFAULT)]
_mods = {k: importlib.import_module(f".mission_{k}", __package__) for k in KEYS}   # a broken file fails at start
KEYS.sort(key=lambda k: (getattr(_mods[k], "ORDER", 99), k))   # course order
if DEFAULT not in _mods:
    raise RuntimeError(f"MISSION={DEFAULT} has no app/mission_{DEFAULT}.py")
# URL names: the key itself, and the mission's SLUG (e.g. "working-with-lists")
ALIASES = {**{k: k for k in KEYS}, **{getattr(m, "SLUG"): k for k, m in _mods.items() if getattr(m, "SLUG", None)}}
RESERVED = {"api", "static", "teacher", "docs", "openapi.json", "redoc", "favicon.ico"}
assert not RESERVED & set(ALIASES), "a mission name clashes with a route"

_current = contextvars.ContextVar("mission", default=DEFAULT)


def resolve(name):
    """The mission key for a URL name, or None."""
    return ALIASES.get((name or "").lower())


def use(key):
    """Make `key` the current mission (for this request / task). Returns a token for reset()."""
    return _current.set(key)


def reset(token):
    _current.reset(token)


def module(key=None):
    return _mods[key or _current.get()]


def slug(key=None):
    key = key or _current.get()
    return getattr(_mods[key], "SLUG", None) or key


def catalog():
    """Every mission this server offers: key, URL name and titles (for the session pickers)."""
    return [{"key": k, "slug": slug(k), "title": _mods[k].UI["title"], "short": _mods[k].UI["short"]} for k in KEYS]


def __getattr__(name):
    # C.MISSION, C.LEVELS, C.QUESTIONS ...: the current mission's value
    if name == "MISSION":
        return _current.get()
    if name.startswith("__"):
        raise AttributeError(name)
    return getattr(_mods[_current.get()], name)
