"""The active mission's content. MISSION picks it (default on this branch: s30, Session 30: Working with Dictionaries).

Each mission module defines LEVELS, QUESTIONS, CONCEPTS, TYPE_LABEL, BADGES, STAGE_BADGE, TOTAL,
LEVEL_BY_ID, VISUAL_PRO (question type, badge id) and UI (texts the pages show).
"""
import importlib
import os

MISSION = os.environ.get("MISSION", "s30").strip().lower() or "s30"  # branch session-30 runs Session 30 by default
_m = importlib.import_module(f".mission_{MISSION}", __package__)
globals().update({k: v for k, v in vars(_m).items() if not k.startswith("_")})
