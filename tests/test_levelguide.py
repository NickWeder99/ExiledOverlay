import json
import os
import sys

# Ensure the repository root is on the Python path when running "pytest" as an
# installed command.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui.modules.levelguide import LevelGuide


def _json_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "levelguide.json")


def test_get_acts_sorted():
    guide = LevelGuide()
    acts = guide.get_acts()
    with open(_json_path(), "r", encoding="utf-8") as f:
        data = json.load(f)
    expected = sorted(data.keys(), key=lambda a: int(a.split(" ")[1]))
    assert acts == expected


def test_tasks_for_act_one():
    guide = LevelGuide()
    tasks = guide.get_tasks_for_act("Act 1")
    with open(_json_path(), "r", encoding="utf-8") as f:
        data = json.load(f)
    expected = data.get("Act 1")
    assert isinstance(tasks, list)
    assert tasks == expected
    assert len(tasks) > 0
