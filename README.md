# About this project

This is a simple CLI program in Python.

It reads CSV and JSONL event files and creates a JSON report.

## Installation

Python 3.12 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## How to use

JSONL:

```bash
python -m streamstats analyze events.jsonl --format jsonl --output report.json
```

CSV:

```bash
python -m streamstats analyze events.csv --format csv --output report.json
```

Several files:

```bash
python -m streamstats analyze first.jsonl second.jsonl --format jsonl
```

Skip invalid records:

```bash
python -m streamstats analyze events.jsonl --format jsonl --skip-invalid
```

Help:

```bash
python -m streamstats --help
python -m streamstats analyze --help
```

The default output file is `report.json`.

## Input

Each event contains `timestamp`, `level`, `source` and `message`.

The timestamp must include a timezone.

Supported levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

CSV files require a header. JSONL files contain one event per line.

## Report

The report contains event counts by level and source, the top 5 sources of ERROR/CRITICAL events, earliest and latest timestamps, and the number of skipped records.

Invalid records stop processing with exit code `2`. With `--skip-invalid`, the program logs warnings and continues.

## Checks

```bash
python -m pytest
ruff check .
```
