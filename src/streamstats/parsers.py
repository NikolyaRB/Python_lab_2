import csv
import json
import logging

import pydantic

from streamstats.errors import (
    InvalidTimestampError,
    InvalidValueError,
    UnknownFormatFileError,
)
from streamstats.models import Event, SkipStats

logger = logging.getLogger(__name__)

# generator for reading a file line by line


def jsonl_reader(
    path: str, skip_stats: SkipStats | None = None, skip_invalid: bool = False
):
    if skip_invalid and skip_stats is None:
        raise ValueError("Stats is required when skip_invalid=True")

    with open(path, "r", encoding="UTF8") as input_file:
        for number, line in enumerate(input_file, start=1):
            # We are attempting to read a line and validate it.
            try:
                event = json.loads(line)
                event_validate = Event.model_validate(event)

            except pydantic.ValidationError as error:
                if skip_invalid:
                    logger.warning(f"Skipped invalid record in {path}: {error}")
                    if skip_stats is not None:
                        skip_stats.skipped_line += 1
                    continue
                else:
                    for err in error.errors():
                        if err["loc"] == ("timestamp",):
                            raise InvalidTimestampError(
                                f"Invalid timestamp on line {number} in file {path}"
                            ) from error
                    raise InvalidValueError(
                        f"Error {error} on line {number} in file {path}"
                    ) from error

            except json.JSONDecodeError as error:
                if skip_invalid:
                    logger.warning(f"Skipped invalid record in {path}: {error}")
                    if skip_stats is not None:
                        skip_stats.skipped_line += 1
                    continue
                else:
                    raise InvalidValueError(
                        f"Error {error} on line {number} in file {path}"
                    ) from error

            yield event_validate


def csv_reader(
    path: str, skip_stats: SkipStats | None = None, skip_invalid: bool = False
):
    if skip_invalid and skip_stats is None:
        raise ValueError("Stats is required when skip_invalid=True")

    with open(path, "r", encoding="UTF8", newline="") as input_file:
        events = csv.DictReader(input_file, strict=True)

        while True:
            # We are attempting to read a line and validate it.
            try:
                event = next(events)
                event_validate = Event.model_validate(event)

            except pydantic.ValidationError as error:
                if skip_invalid:
                    logger.warning(f"Skipped invalid record in {path}: {error}")
                    if skip_stats is not None:
                        skip_stats.skipped_line += 1
                    continue
                else:
                    number = events.reader.line_num
                    for err in error.errors():
                        if err["loc"] == ("timestamp",):
                            raise InvalidTimestampError(
                                f"Invalid timestamp on line {number} in file {path}"
                            ) from error
                    raise InvalidValueError(
                        f"Error {error} on line {number} in file {path}"
                    ) from error

            except csv.Error as error:
                if skip_invalid:
                    logger.warning(f"Skipped invalid record in {path}: {error}")
                    if skip_stats is not None:
                        skip_stats.skipped_line += 1
                    continue
                else:
                    number = events.reader.line_num
                    raise InvalidValueError(
                        f"Error {error} on line {number} in file {path}"
                    ) from error

            except StopIteration:
                break

            yield event_validate


def files_reader(
    paths: list[str],
    file_format: str,
    skip_stats: SkipStats | None = None,
    skip_invalid: bool = False,
):
    if file_format == "jsonl":
        for path in paths:
            yield from jsonl_reader(path, skip_stats, skip_invalid)
    elif file_format == "csv":
        for path in paths:
            yield from csv_reader(path, skip_stats, skip_invalid)
    else:
        raise UnknownFormatFileError
