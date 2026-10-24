import datetime
import typing

import pydantic


class Event(pydantic.BaseModel):
    timestamp: pydantic.AwareDatetime
    level: typing.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    source: str = pydantic.Field(min_length=1)
    message: str


class SkipStats:
    def __init__(self):
        self.skipped_line = 0


class AnalysisStats:
    total: int
    count_by_level: dict[str, int]
    count_by_source: dict[str, int]
    top_error_sources: dict[str, int]
    error_count_by_source: dict[str, int]
    first_timestamp: datetime.datetime | None
    last_timestamp: datetime.datetime | None

    def __init__(self):
        self.total = 0
        self.count_by_level = {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0,
        }
        self.count_by_source = {}
        self.top_error_sources = {}
        self.error_count_by_source = {}
        self.first_timestamp = None
        self.last_timestamp = None
