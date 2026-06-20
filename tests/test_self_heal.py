import sys
import tempfile
from pathlib import Path

import pytest

from farewell_assistant.self_heal import _run_check, _has_marker

PY = "py" if sys.platform == "win32" else "python"


class TestRunCheck:
    def test_success(self):
        passed, output = _run_check([PY, "-c", "print('ok')"])
        assert passed is True

    def test_failure(self):
        passed, output = _run_check([PY, "-c", "import sys; sys.exit(1)"])
        assert passed is False

    def test_failure_with_pattern_match(self):
        # Command fails AND error pattern IS in output → fail
        passed, output = _run_check(
            [PY, "-c", "print('error: syntax'); import sys; sys.exit(1)"],
            check_pattern="error"
        )
        assert passed is False

    def test_failure_with_pattern_not_in_output(self):
        # Command fails but error pattern NOT in output → pass (relaxed)
        passed, output = _run_check(
            [PY, "-c", "import sys; sys.exit(1)"],
            check_pattern="syntax error"
        )
        assert passed is True

    def test_command_not_found(self):
        passed, output = _run_check(["nonexistent_command_xyz_12345"])
        assert passed is False


class TestHasMarker:
    def test_marker_exists(self, tmp_path):
        (tmp_path / "package.json").write_text("{}")
        assert _has_marker(tmp_path, ["package.json"]) is True

    def test_no_marker(self, tmp_path):
        assert _has_marker(tmp_path, ["package.json"]) is False
