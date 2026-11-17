"""
Helpers for signal stats and analytics widgets.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from django.db.models import Count, Sum
from django.db.models.functions import ExtractHour, TruncDate

from apps.events.models import SignalEntry
from apps.signals.models import AverageWeighting, Signal, SignalType, SummaryMethod

from .models import AnalyticsWidget, WidgetAggregation, WidgetTimeframe, WidgetType

TIMEFRAMES = ('week', 'month', 'quarter', 'year')

UTC = ZoneInfo('UTC')


@dataclass
class Period:
    timeframe: str
    tz: ZoneInfo
    start_local: date   # inclusive
    end_local: date     # exclusive
    start_utc: datetime # inclusive, for filtering occurred_at
    end_utc: datetime   # exclusive, for filtering occurred_at


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    return d.replace(year=year, month=month, day=1)


def resolve_period(timeframe: str, period_start: date, tz: ZoneInfo) -> Period:
    """
    Resolve the local calendar range for a timeframe.
    """
    if timeframe == 'week':
        start_local = period_start - timedelta(days=period_start.weekday())  # Monday
        end_local = start_local + timedelta(days=7)
    elif timeframe == 'month':
        start_local = period_start.replace(day=1)
        end_local = _add_months(start_local, 1)
    elif timeframe == 'quarter':
        quarter_start_month = ((period_start.month - 1) // 3) * 3 + 1
        start_local = period_start.replace(month=quarter_start_month, day=1)
        end_local = _add_months(start_local, 3)
    elif timeframe == 'year':
        start_local = period_start.replace(month=1, day=1)
        end_local = start_local.replace(year=start_local.year + 1)
    else:
        raise ValueError(f'Unknown timeframe: {timeframe}')

    return _make_period(timeframe, start_local, end_local, tz)


def _make_period(timeframe: str, start_local: date, end_local: date, tz: ZoneInfo) -> Period:
    start_utc = datetime.combine(start_local, datetime.min.time(), tzinfo=tz).astimezone(UTC)
    end_utc = datetime.combine(end_local, datetime.min.time(), tzinfo=tz).astimezone(UTC)

    return Period(
        timeframe=timeframe,
        tz=tz,
        start_local=start_local,
        end_local=end_local,
        start_utc=start_utc,
        end_utc=end_utc,
    )


def resolve_widget_period(widget: AnalyticsWidget, tz: ZoneInfo) -> Period:
    """
    Resolve timeframe relative to local tz.
    """
    today = datetime.now(tz).date()
    timeframe = widget.timeframe

    if timeframe == WidgetTimeframe.TODAY:
        return _make_period(timeframe, today, today + timedelta(days=1), tz)
    if timeframe == WidgetTimeframe.YESTERDAY:
        return _make_period(timeframe, today - timedelta(days=1), today, tz)
    if timeframe == WidgetTimeframe.LAST_DAYS:
        start_local = today - timedelta(days=widget.days - 1)
        return _make_period(timeframe, start_local, today + timedelta(days=1), tz)
    if timeframe == WidgetTimeframe.THIS_WEEK:
        return resolve_period('week', today, tz)
    if timeframe == WidgetTimeframe.LAST_WEEK:
        return resolve_period('week', today - timedelta(days=7), tz)
    if timeframe == WidgetTimeframe.THIS_MONTH:
        return resolve_period('month', today, tz)
    if timeframe == WidgetTimeframe.LAST_MONTH:
        return resolve_period('month', today.replace(day=1) - timedelta(days=1), tz)
    if timeframe == WidgetTimeframe.THIS_QUARTER:
        return resolve_period('quarter', today, tz)
    if timeframe == WidgetTimeframe.QUARTER:
        return resolve_period('quarter', widget.period_start, tz)
    if timeframe == WidgetTimeframe.THIS_YEAR:
        return resolve_period('year', today, tz)
    if timeframe == WidgetTimeframe.YEAR:
        return resolve_period('year', widget.period_start, tz)
    raise ValueError(f'Unknown widget timeframe: {timeframe}')


def get_widget_values(widget: AnalyticsWidget, user, tz: ZoneInfo) -> dict:
    """
    Data for one widget, shaped by its type. 'timeseries' is only filled for over time widgets.
    """
    period = resolve_widget_period(widget, tz)
    rows = _bin_rows(widget.signal, user, period)
    totals = _totals(rows, widget.signal)
    is_timeseries = widget.type == WidgetType.TIMESERIES

    if is_timeseries:
        value = None
    elif widget.aggregation == WidgetAggregation.AVERAGE:
        value = totals['average'] if totals['count'] else None
    else:
        value = totals['total']

    return {
        'widget_id': widget.id,
        'value': value,
        'count': totals['count'],
        'period': {'start': period.start_local.isoformat(), 'end': period.end_local.isoformat()},
        'timeseries': _timeseries(rows, widget.signal, period) if is_timeseries else None,
    }


def get_signal_stats(signal: Signal, user, period: Period) -> dict:
    rows = _bin_rows(signal, user, period)
    return {
        **_totals(rows, signal),
        'timeseries': _timeseries(rows, signal, period),
        'day_of_week': _day_of_week(rows, signal),
        'heatmap': _heatmap(rows, signal),
    }


def signal_value_field(signal: Signal) -> str:
    return 'duration' if signal.type == SignalType.DURATION else 'value'


def _to_number(value) -> float:
    if value is None:
        return 0.0
    return value.total_seconds() if isinstance(value, timedelta) else float(value)


def _bin_rows(signal: Signal, user, period: Period) -> list[tuple[date, int, float, int]]:
    """
    One query for all stats: (local date, local hour, sum, entry count) for every
    day/hour bin with entries in the period. Totals, timeseries, day of week and
    heatmap are all derived from these (at most 24 rows per day).
    """
    rows = (
        SignalEntry.objects.filter(
            signal=signal,
            event__user=user,
            event__occurred_at__gte=period.start_utc,
            event__occurred_at__lt=period.end_utc,
        )
        .annotate(
            day=TruncDate('event__occurred_at', tzinfo=period.tz),
            hour=ExtractHour('event__occurred_at', tzinfo=period.tz),
        )
        .values('day', 'hour')
        .annotate(total=Sum(signal_value_field(signal)), count=Count('id'))
    )
    return [(r['day'], r['hour'], _to_number(r['total']), r['count']) for r in rows]


def _mean(days: dict, signal: Signal) -> float:
    """
    Mean of the numbers behind days = {day: [sum, count]}, following signal.average_weighting:
    one mean over all events, or the mean of the daily means (days without events are not in days).
    """
    if signal.average_weighting == AverageWeighting.DAY:
        return sum(t / c for t, c in days.values()) / len(days)
    return sum(t for t, _ in days.values()) / sum(c for _, c in days.values())


def _by_day(rows) -> dict:
    days = defaultdict(lambda: [0.0, 0])
    for day, _hour, total, count in rows:
        days[day][0] += total
        days[day][1] += count
    return days


def _totals(rows, signal: Signal) -> dict:
    days = _by_day(rows)
    total = sum(t for t, _ in days.values())
    count = sum(c for _, c in days.values())
    return {'total': total, 'average': _mean(days, signal) if count else 0.0, 'count': count}


def _grouped(rows, signal: Signal, key) -> dict:
    """
    Bins the rows by key(day, hour) and applies the signals summary_method: the sum, or the
    average (see _mean) of the entries in the bin. Bins without entries are not in the result.
    Returns {key: (value, entry count)}.
    """
    bins = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    for day, hour, total, count in rows:
        b = bins[key(day, hour)][day]
        b[0] += total
        b[1] += count
    average = signal.summary_method == SummaryMethod.AVERAGE
    return {
        k: (_mean(days, signal) if average else sum(t for t, _ in days.values()),
            sum(c for _, c in days.values()))
        for k, days in bins.items()
    }


def _empty_bucket_value(signal: Signal) -> float | None:
    """
    Value of a bucket with no entries: 0 for sum signals, None for average signals.
    """
    return None if signal.summary_method == SummaryMethod.AVERAGE else 0.0


def _timeseries(rows, signal: Signal, period: Period) -> list[dict]:
    """
    One row per local calendar day in the period. The daily value follows the
    signal's summary_method (sum or average). Days without entries are 0 for sum signals
    and None for average signals.
    """
    by_day = _grouped(rows, signal, lambda day, hour: day)
    raw = _by_day(rows)
    if signal.summary_method == SummaryMethod.AVERAGE and signal.average_weighting == AverageWeighting.DAY:
        raw = {day: [by_day[day][0], 1] for day in raw}
    empty = _empty_bucket_value(signal)
    return [
        {
            'date': day.isoformat(),
            'value': by_day[day][0] if day in by_day else empty,
            'sum': raw[day][0] if day in raw else 0.0,
            'count': raw[day][1] if day in raw else 0,
        }
        for day in (period.start_local + timedelta(days=i) for i in range((period.end_local - period.start_local).days))
    ]


def _day_of_week(rows, signal: Signal) -> list[dict]:
    """
    Value per day of week (0=Monday, 6=Sunday), following the signals summary_method.
    """
    by_dow = _grouped(rows, signal, lambda day, hour: day.weekday())
    empty = _empty_bucket_value(signal)
    return [{'dow': dow, 'value': by_dow[dow][0] if dow in by_dow else empty} for dow in range(7)]


def _heatmap(rows, signal: Signal) -> list[dict]:
    """
    Heatmap with day of week/hour bins: sum or average of the entries values in the bin.
    """
    return [
        {'dow': dow, 'hour': hour, 'count': count, 'value': value}
        for (dow, hour), (value, count) in _grouped(rows, signal, lambda day, hour: (day.weekday(), hour)).items()
    ]
