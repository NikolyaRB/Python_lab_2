from streamstats.models import AnalysisStats


def analyze(events) -> AnalysisStats:
    # let's create an object of the statistics class
    analys_stats = AnalysisStats()
    for event in events:
        # counting the total number of events
        analys_stats.total += 1
        # counting the number of events of each level
        analys_stats.count_by_level[event.level] += 1
        # counting the number of events from each source
        analys_stats.count_by_source[event.source] = (
            analys_stats.count_by_source.get(event.source, 0) + 1
        )

        # finding the first timestamp
        if analys_stats.first_timestamp is None:
            analys_stats.first_timestamp = event.timestamp
        else:
            analys_stats.first_timestamp = min(
                analys_stats.first_timestamp, event.timestamp
            )

        # finding the last timestamp
        if analys_stats.last_timestamp is None:
            analys_stats.last_timestamp = event.timestamp
        else:
            analys_stats.last_timestamp = max(
                analys_stats.last_timestamp, event.timestamp
            )
        # counting the number of CRITICAL and ERROR events
        if event.level in ["ERROR", "CRITICAL"]:
            analys_stats.error_count_by_source[event.source] = (
                analys_stats.error_count_by_source.get(event.source, 0) + 1
            )

    # identifying the top 5 event sources
    error_source = []
    for [key, value] in analys_stats.error_count_by_source.items():
        error_source.append([value, key])

    error_source.sort(key=lambda item: (-item[0], item[1]))
    for [value, key] in error_source[:5]:
        analys_stats.top_error_sources[key] = value

    return analys_stats
