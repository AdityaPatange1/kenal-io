"""Tests for kenal.cli."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from kenal.cli import main


class TestCLIInfo:
    def test_info(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("sys.argv", ["kenal", "info"])
        assert main() == 0
        out = capsys.readouterr().out
        assert "kenal" in out
        assert "Block" in out


class TestCLIVersion:
    def test_version(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("sys.argv", ["kenal", "--version"])
        with pytest.raises(SystemExit, match="0"):
            main()


class TestCLIRun:
    def test_run_config(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = {
            "blocks": [
                {"name": "upper", "rules": []},
            ],
            "plates": [],
            "roads": [],
            "frame": {"name": "test"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as fh:
            json.dump(config, fh)
            fh.flush()
            path = fh.name

        try:
            b_process = lambda d: d.upper() if isinstance(d, str) else d  # noqa: E731

            def patched_run(config_path: str, input_data: str) -> int:
                from kenal.block import Block
                from kenal.frame import Frame

                blk = Block(name="upper", process=b_process)
                f = Frame(name="test", blocks=[blk])
                results = f.run(input_data)
                for r in results:
                    print(f"[{r.source_block}] {r.output}")
                return 0

            monkeypatch.setattr("kenal.cli._run_config", patched_run)
            monkeypatch.setattr("sys.argv", ["kenal", "run", path, "hello"])
            assert main() == 0
            out = capsys.readouterr().out
            assert "HELLO" in out
        finally:
            os.unlink(path)

    def test_bad_config_path(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("sys.argv", ["kenal", "run", "/nonexistent.json", "input"])
        assert main() == 1
        err = capsys.readouterr().err
        assert "Error" in err
