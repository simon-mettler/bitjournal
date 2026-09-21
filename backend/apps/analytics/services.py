"""
Helpers for signal stats. Reads from 'events' and 'signals'.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from django.db.models import Avg, Count, Sum
from django.db.models.functions import Extract, TruncDate

from apps.events.models import SignalEntry
from apps.signals.models import Signal, SignalType, SummaryMethod

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


def signal_value_field(signal: Signal) -> str:
    return 'duration' if signal.type == SignalType.DURATION else 'value'


def _to_number(value, is_duration: bool) -> float:
    if value is None:
        return 0.0
    return value.total_seconds() if is_duration else float(value)


def _summary_aggregate(signal: Signal, field: str):
    """Aggregate for one bucket (day), following the signals summary_method."""
    if signal.summary_method == SummaryMethod.AVERAGE:
        return Avg(field)
    return Sum(field)


def _empty_bucket_value(signal: Signal) -> float | None:
    """
    Value of a bucket with no entries: 0 for sum signals, None for average signals.
    """
    return None if signal.summary_method == SummaryMethod.AVERAGE else 0.0


def entries_in_period(signal: Signal, user, period: Period):
    return SignalEntry.objects.filter(
        signal=signal,
        event__user=user,
        event__occurred_at__gte=period.start_utc,
        event__occurred_at__lt=period.end_utc,
    )


def get_signal_totals(signal: Signal, user, period: Period) -> dict:
    field = signal_value_field(signal)
    is_duration = field == 'duration'

    aggregates = entries_in_period(signal, user, period).aggregate(
        total=Sum(field),
        average=Avg(field),
        count=Count('id'),
    )

    return {
        'total': _to_number(aggregates['total'], is_duration),
        'average': _to_number(aggregates['average'], is_duration),
        'count': aggregates['count'] or 0,
    }


def get_signal_timeseries(signal: Signal, user, period: Period) -> list[dict]:
    """
    One row per local calendar day in the period. The daily value follows the
    signal's summary_method (sum or average). Days without entries are 0 for sum signals
    and None for average signals.
    """
    field = signal_value_field(signal)
    is_duration = field == 'duration'
    empty = _empty_bucket_value(signal)

    rows = (
        entries_in_period(signal, user, period)
        .annotate(day=TruncDate('event__occurred_at', tzinfo=period.tz))
        .values('day')
        .annotate(value=_summary_aggregate(signal, field))
    )
    values_by_day = {row['day']: _to_number(row['value'], is_duration) for row in rows}

    timeseries = []
    current = period.start_local
    while current < period.end_local:
        timeseries.append({
            'date': current.isoformat(),
            'value': values_by_day.get(current, empty),
        })
        current += timedelta(days=1)

    return timeseries


def get_signal_day_of_week(signal: Signal, user, period: Period) -> list[dict]:
    """
    Value per day of week (0=Monday, 6=Sunday), following the signals
    summary_method: sum, or average over all entries on that weekday.
    """
    field = signal_value_field(signal)
    is_duration = field == 'duration'
    empty = _empty_bucket_value(signal)

    rows = (
        entries_in_period(signal, user, period)
        .annotate(pg_dow=Extract('event__occurred_at', 'dow', tzinfo=period.tz))
        .values('pg_dow')
        .annotate(value=_summary_aggregate(signal, field))
    )
    values_by_iso_dow = {
        int(row['pg_dow'] + 6) % 7: _to_number(row['value'], is_duration)
        for row in rows
    }

    return [
        {'dow': dow, 'value': values_by_iso_dow.get(dow, empty)}
        for dow in range(7)
    ]


def get_signal_heatmap(signal: Signal, user, period: Period) -> list[dict]:
    """
    Heatmap with day of week/hour bins: sum or average of the entries values in the bin.
    """
    field = signal_value_field(signal)
    is_duration = field == 'duration'

    rows = (
        entries_in_period(signal, user, period)
        .annotate(
            pg_dow=Extract('event__occurred_at', 'dow', tzinfo=period.tz),
            hour=Extract('event__occurred_at', 'hour', tzinfo=period.tz),
        )
        .values('pg_dow', 'hour')
        .annotate(count=Count('id'), value=_summary_aggregate(signal, field))
    )

    return [
        {
            'dow': int(row['pg_dow'] + 6) % 7,
            'hour': int(row['hour']),
            'count': row['count'],
            'value': _to_number(row['value'], is_duration),
        }
        for row in rows
    ]
