import json

import pytest
from typer.testing import CliRunner

from streamstats.__main__ import app
from streamstats.analysis import analyze
from streamstats.errors import InvalidValueError
from streamstats.models import SkipStats
from streamstats.parsers import csv_reader, files_reader, jsonl_reader


def test_jsonl_reader(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"INFO","source":"api","message":"start"}\n',
        encoding="utf-8",
    )

    events = list(jsonl_reader(str(path)))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "api"
    assert events[0].message == "start"
    assert events[0].timestamp.isoformat() == "2026-10-20T13:00:00+03:00"


def test_csv_reader(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,level,source,message\n2026-10-20T13:00:00+03:00,INFO,api,start\n",
        encoding="utf-8",
    )

    events = list(csv_reader(str(path)))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "api"
    assert events[0].message == "start"
    assert events[0].timestamp.isoformat() == "2026-10-20T13:00:00+03:00"


def test_jsonl_reader_empty_file(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")

    assert list(jsonl_reader(str(path))) == []


def test_csv_reader_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    assert list(csv_reader(str(path))) == []


def test_jsonl_invalid_file_not_skipped(tmp_path):
    path = tmp_path / "invalid.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"HELLO","source":"api","message":"bad"}\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidValueError):
        list(jsonl_reader(str(path), skip_invalid=False))


def test_csv_invalid_file_not_skipped(tmp_path):
    path = tmp_path / "invalid.csv"
    path.write_text(
        "timestamp,level,source,message\n2026-10-20T13:00:00+03:00,HELLO,api,bad\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidValueError):
        list(csv_reader(str(path), skip_invalid=False))


def test_jsonl_invalid_file_skipped(tmp_path, caplog):
    path = tmp_path / "invalid.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"HELLO","source":"api","message":"bad"}\n'
        '{"timestamp":"2026-10-20T14:00:00+03:00",'
        '"level":"INFO","source":"api","message":"start"}\n',
        encoding="utf-8",
    )

    skip_stats = SkipStats()
    events = list(jsonl_reader(str(path), skip_stats, skip_invalid=True))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "api"
    assert events[0].message == "start"
    assert skip_stats.skipped_line == 1

    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) == 1


def test_csv_invalid_file_skipped(tmp_path, caplog):
    path = tmp_path / "invalid.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T13:00:00+03:00,HELLO,api,bad\n"
        "2026-10-20T14:00:00+03:00,INFO,api,start\n",
        encoding="utf-8",
    )

    skip_stats = SkipStats()
    events = list(csv_reader(str(path), skip_stats, skip_invalid=True))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "api"
    assert events[0].message == "start"
    assert skip_stats.skipped_line == 1

    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) == 1


def test_unite_jsonl_files(tmp_path):
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"

    first.write_text(
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"INFO","source":"api","message":"start"}\n',
        encoding="utf-8",
    )
    second.write_text(
        '{"timestamp":"2026-10-20T12:00:00+03:00",'
        '"level":"ERROR","source":"api","message":"failed"}\n',
        encoding="utf-8",
    )

    events = files_reader([str(first), str(second)], "jsonl")
    stats = analyze(events)

    assert stats.total == 2
    assert stats.count_by_level["INFO"] == 1
    assert stats.count_by_level["ERROR"] == 1
    assert stats.count_by_source == {"api": 2}
    assert stats.top_error_sources == {"api": 1}
    assert stats.first_timestamp.isoformat() == "2026-10-20T12:00:00+03:00"
    assert stats.last_timestamp.isoformat() == "2026-10-20T13:00:00+03:00"


def test_unite_csv_files(tmp_path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"

    first.write_text(
        "timestamp,level,source,message\n2026-10-20T13:00:00+03:00,INFO,api,start\n",
        encoding="utf-8",
    )
    second.write_text(
        "timestamp,level,source,message\n2026-10-20T12:00:00+03:00,ERROR,api,failed\n",
        encoding="utf-8",
    )

    events = files_reader([str(first), str(second)], "csv")
    stats = analyze(events)

    assert stats.total == 2
    assert stats.count_by_level["INFO"] == 1
    assert stats.count_by_level["ERROR"] == 1
    assert stats.count_by_source == {"api": 2}
    assert stats.top_error_sources == {"api": 1}
    assert stats.first_timestamp.isoformat() == "2026-10-20T12:00:00+03:00"
    assert stats.last_timestamp.isoformat() == "2026-10-20T13:00:00+03:00"


def test_jsonl_unicode(tmp_path):
    path = tmp_path / "unicode.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"INFO","source":"api","message":"Started 💯"}\n',
        encoding="utf-8",
    )

    events = list(jsonl_reader(str(path)))

    assert len(events) == 1
    assert events[0].message == "Started 💯"


def test_csv_unicode(tmp_path):
    path = tmp_path / "unicode.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T13:00:00+03:00,INFO,api,Started 💯\n",
        encoding="utf-8",
        newline="",
    )

    events = list(csv_reader(str(path)))

    assert len(events) == 1
    assert events[0].message == "Started 💯"


def test_cli_report(tmp_path):
    path = tmp_path / "events.jsonl"
    output = tmp_path / "report.json"
    path.write_text(
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"INFO","source":"api","message":"start"}\n',
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "analyze",
            str(path),
            "--format",
            "jsonl",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output

    data = json.loads(output.read_text(encoding="utf-8"))

    assert data["total"] == 1
    assert data["count_by_level"] == {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }
    assert data["count_by_source"] == {"api": 1}
    assert data["top_error_sources"] == {}
    assert data["first_timestamp"] == "2026-10-20T13:00:00+03:00"
    assert data["last_timestamp"] == "2026-10-20T13:00:00+03:00"
    assert data["skipped"] == 0


def test_cli_invalid_file(tmp_path):
    path = tmp_path / "invalid.jsonl"
    output = tmp_path / "report.json"
    path.write_text(
        '{"timestamp":"2026-10-20T13:00:00+03:00",'
        '"level":"HELLO","source":"api","message":"bad"}\n',
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "analyze",
            str(path),
            "--format",
            "jsonl",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 2, result.output
    assert "Error:" in result.output
    assert str(path) in result.output
    assert "on line 1" in result.output
