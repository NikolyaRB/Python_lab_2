import json

from streamstats.models import AnalysisStats, SkipStats


def report(
    analys_stats: AnalysisStats, skip_stats: SkipStats, output_path: str
) -> None:
    first_timestamp = None
    last_timestamp = None

    if analys_stats.first_timestamp is not None:
        first_timestamp = analys_stats.first_timestamp.isoformat()

    if analys_stats.last_timestamp is not None:
        last_timestamp = analys_stats.last_timestamp.isoformat()

    report_data = {
        "total": analys_stats.total,
        "count_by_level": analys_stats.count_by_level,
        "count_by_source": analys_stats.count_by_source,
        "top_error_sources": analys_stats.top_error_sources,
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "skipped": skip_stats.skipped_line,
    }

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(report_data, output_file, ensure_ascii=False, indent=4)
