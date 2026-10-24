class StreamStatsError(Exception):
    pass


class InvalidValueError(StreamStatsError):
    pass


class UnknownFormatFileError(StreamStatsError):
    pass


class InvalidTimestampError(StreamStatsError):
    pass
