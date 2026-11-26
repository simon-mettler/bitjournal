"""
Helpers for signal stats and analytics widgets.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import cached_property
from zoneinfo import ZoneInfo

from django.db.models import Count, Min, Sum
from django.db.models.functions import ExtractHour, TruncDate

from apps.events.models import SignalEntry
from apps.signals.models import AverageWeighting, Signal, SignalType, SummaryMethod

from .models import AnalyticsWidget, WidgetTimeframe

TIMEFRAMES = ('week', 'month', 'quarter', 'year')

UTC = ZoneInfo('UTC')

# Periods longer than this are shown in weekly steps (365 daily bars are too dense to read).
WEEKLY_STEP_MIN_DAYS = 100
# Number of steps (the current one and the ones before it) behind one point of the trend line.
TREND_WINDOW = {'day': 7, 'week': 4}

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


def resolve_widget_period(widget: AnalyticsWidget, tz: ZoneInfo, today: date) -> Period:
    """
    Resolve timeframe relative to today, the current date in tz.
    """
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


class WidgetData:
    """What the widget type definitions build their data from."""

    def __init__(self, widget: AnalyticsWidget, user, period: Period, today: date):
        self.signal = widget.signal
        self.config = widget.settings
        self.period = period
        self.today = today
        self.first_day = _first_entry_day(widget.signal, user, period.tz)
        self._all_rows = _bin_rows(widget.signal, user, _with_trend_lookback(period))
        self._rows = _within(self._all_rows, period)

    @cached_property
    def totals(self) -> dict:
        return _totals(self._rows, self.signal, self.period, self.first_day, self.today)

    def timeseries(self) -> dict:
        return _timeseries(self._all_rows, self.signal, self.period, self.first_day, self.today)


def get_widget_values(widget: AnalyticsWidget, user, tz: ZoneInfo) -> dict:
    """
    Data for one widget: the period and entry count, plus 'value' and 'timeseries'
    as filled by the widget's type.
    """
    today = datetime.now(tz).date()
    period = resolve_widget_period(widget, tz, today)
    data = WidgetData(widget, user, period, today)

    return {
        'widget_id': widget.id,
        'count': data.totals['count'],
        'period': {'start': period.start_local.isoformat(), 'end': period.end_local.isoformat()},
        **widget.definition.data(data),
    }


def get_signal_stats(signal: Signal, user, period: Period, today: date | None = None) -> dict:
    today = today or datetime.now(period.tz).date()
    first_day = _first_entry_day(signal, user, period.tz)
    all_rows = _bin_rows(signal, user, _with_trend_lookback(period))
    rows = _within(all_rows, period)
    return {
        **_totals(rows, signal, period, first_day, today),
        'timeseries': _timeseries(all_rows, signal, period, first_day, today),
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


def _week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())  # Monday


def _step(period: Period) -> str:
    return 'week' if (period.end_local - period.start_local).days > WEEKLY_STEP_MIN_DAYS else 'day'


def _with_trend_lookback(period: Period) -> Period:
    """
    The period widened by the data the trend line needs: the steps before the first one and,
    for weekly steps, the full calendar weeks at both edges.
    """
    window = TREND_WINDOW[_step(period)]
    if _step(period) == 'day':
        start, end = period.start_local - timedelta(days=window - 1), period.end_local
    else:
        start = _week_start(period.start_local) - timedelta(weeks=window - 1)
        end = _week_start(period.end_local - timedelta(days=1)) + timedelta(weeks=1)
    return _make_period(period.timeframe, start, end, period.tz)


def _within(rows, period: Period) -> list:
    return [row for row in rows if period.start_local <= row[0] < period.end_local]


def _first_entry_day(signal: Signal, user, tz: ZoneInfo) -> date | None:
    """
    Local date of the signal's first entry. Total signals only count empty days as 0 from then on.
    """
    first = SignalEntry.objects.filter(signal=signal, event__user=user).aggregate(
        first=Min('event__occurred_at'))['first']
    return first and first.astimezone(tz).date()


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


def _per_day(days: dict, period: Period, first_day: date | None, today: date) -> float:
    """
    Total per day over the completed days of the period since the first entry, including days
    without entries. Today is unfinished and only used if there is no completed day.
    """
    if first_day is None:
        return 0.0
    start = max(period.start_local, first_day)
    end = min(period.end_local, today)
    if end <= start:
        return days[today][0] if today in days else 0.0
    return sum(t for day, (t, _) in days.items() if start <= day < end) / (end - start).days


def _totals(rows, signal: Signal, period: Period, first_day: date | None, today: date) -> dict:
    """
    Total, average and entry count of the period. The average of a total signal is per day,
    the one of an average signal follows its average_weighting.
    """
    days = _by_day(rows)
    total = sum(t for t, _ in days.values())
    count = sum(c for _, c in days.values())
    if signal.summary_method == SummaryMethod.SUM:
        average = _per_day(days, period, first_day, today)
    else:
        average = _mean(days, signal) if count else 0.0
    return {'total': total, 'average': average, 'count': count}


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


def _dates(start: date, end: date) -> list[date]:
    """Days from start (inclusive) to end (exclusive)."""
    return [start + timedelta(days=i) for i in range((end - start).days)]


def _step_value(days: dict, span: list[date], signal: Signal, first_day: date | None, today: date) -> float | None:
    """
    Value of one step: sum or average of its entries. Without entries it is None, except for
    total signals on days that have passed since the first entry, which are a real 0.
    """
    found = {day: days[day] for day in span if day in days}
    if signal.summary_method == SummaryMethod.AVERAGE:
        return _mean(found, signal) if found else None
    if found:
        return sum(t for t, _ in found.values())
    tracked = first_day is not None and span[-1] >= first_day and span[0] <= today
    return 0.0 if tracked else None


def _trend_value(days: dict, start: date, length: int, window: int, signal: Signal,
                 first_day: date | None, today: date) -> float | None:
    """
    Moving average at the step of `length` days beginning at start, over it and the steps before.
    Average signals: mean of the entries in the window. Total signals: mean step total, only
    counting steps that are over and began on or after the first entry.
    """
    if start > today:
        return None
    starts = [start - timedelta(days=length * i) for i in range(window)]
    spans = [_dates(s, s + timedelta(days=length)) for s in starts]
    if signal.summary_method == SummaryMethod.AVERAGE:
        found = {day: days[day] for span in spans for day in span if day in days}
        return _mean(found, signal) if found else None

    def is_complete(span):
        return first_day is not None and span[0] >= first_day and span[-1] < today

    if spans[0][-1] >= today:  # no trend point on the unfinished step
        return None
    totals = [sum(days[day][0] for day in span if day in days) for span in spans if is_complete(span)]
    return sum(totals) / len(totals) if totals else None


def _timeseries(rows, signal: Signal, period: Period, first_day: date | None, today: date) -> dict:
    """
    The period in daily or weekly steps (weeks start Monday and are clipped to the period).
    Rows must include the trend lookback, see _with_trend_lookback.
    """
    step = _step(period)
    length = 7 if step == 'week' else 1
    days = _by_day(rows)

    spans = defaultdict(list)
    for day in _dates(period.start_local, period.end_local):
        spans[_week_start(day) if step == 'week' else day].append(day)

    points = []
    for step_start, span in spans.items():
        value = _step_value(days, span, signal, first_day, today)
        partial = (
            signal.summary_method == SummaryMethod.SUM
            and value is not None
            and (
                len(span) < length
                or span[0] <= today <= span[-1]
                or (first_day is not None and span[0] < first_day <= span[-1])
            )
        )
        points.append({
            'start': span[0].isoformat(),
            'end': span[-1].isoformat(),
            'value': value,
            'trend': _trend_value(days, step_start, length, TREND_WINDOW[step], signal, first_day, today),
            'partial': partial,
        })
    return {'step': step, 'points': points}


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
