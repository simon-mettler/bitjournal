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
from apps.signals.models import Signal, SignalType, SummaryMethod

from .calculations import default_calculation, supported_calculation
from .models import AnalyticsWidget, WidgetCalculation, WidgetTimeframe

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
        self.calculation = supported_calculation(widget.signal, self.config['calculation'])
        self.period = period
        self.today = today
        self.first_day = _first_entry_day(widget.signal, user, period.tz)
        self._all_rows = _bin_rows(widget.signal, user, _with_trend_lookback(period))
        self._rows = _within(self._all_rows, period)

    @cached_property
    def totals(self) -> dict:
        return _totals(self._rows, self.signal, self.period, self.first_day, self.today)

    def timeseries(self) -> dict:
        return _timeseries(
            self._all_rows, self.signal, self.calculation, self.period, self.first_day, self.today)


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


def get_signal_stats(signal: Signal, user, period: Period, today: date | None = None,
                     calculation: str | None = None) -> dict:
    today = today or datetime.now(period.tz).date()
    calculation = calculation or default_calculation(signal)
    first_day = _first_entry_day(signal, user, period.tz)
    all_rows = _bin_rows(signal, user, _with_trend_lookback(period))
    rows = _within(all_rows, period)
    return {
        **_totals(rows, signal, period, first_day, today),
        'calculation': calculation,
        'timeseries': _timeseries(all_rows, signal, calculation, period, first_day, today),
        'day_of_week': _day_of_week(rows, signal, calculation, period, first_day, today),
        'heatmap': _heatmap(rows, signal, calculation),
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
    Local date of the signal's first entry. Empty days only count as 0 from then on.
    """
    first = SignalEntry.objects.filter(signal=signal, event__user=user).aggregate(
        first=Min('event__occurred_at'))['first']
    return first and first.astimezone(tz).date()


def _by_day(rows) -> dict:
    days = defaultdict(lambda: [0.0, 0])
    for day, _hour, total, count in rows:
        days[day][0] += total
        days[day][1] += count
    return days


def _sum(days: dict) -> float:
    return sum(t for t, _ in days.values())


def _entry_mean(days: dict) -> float | None:
    count = sum(c for _, c in days.values())
    return _sum(days) / count if count else None


def _mean_of_daily_means(days: dict) -> float | None:
    return sum(t / c for t, c in days.values()) / len(days) if days else None


def _tracked(day: date, first_day: date | None, today: date) -> bool:
    return first_day is not None and first_day <= day < today


def _daily_values(days: dict, signal: Signal) -> dict:
    if signal.summary_method == SummaryMethod.SUM:
        return {day: total for day, (total, _) in days.items()}
    return {day: total / count for day, (total, count) in days.items()}


def _per_tracked_day(values: dict, span: list[date], first_day: date | None, today: date) -> float | None:
    tracked = [day for day in span if _tracked(day, first_day, today)]
    if tracked:
        return sum(values.get(day, 0.0) for day in tracked) / len(tracked)
    if today in span and first_day is not None and first_day <= today:
        return values.get(today, 0.0)
    found = [values[day] for day in span if day in values]
    return sum(found) / len(found) if found else None


def _daily_average(days: dict, span: list[date], signal: Signal, first_day: date | None,
                   today: date) -> float | None:
    values = _daily_values(days, signal)
    if signal.counts_empty_days_as_zero:
        return _per_tracked_day(values, span, first_day, today)
    found = [values[day] for day in span if day in values]
    return sum(found) / len(found) if found else None


def _totals(rows, signal: Signal, period: Period, first_day: date | None, today: date) -> dict:
    days = _by_day(rows)
    # future days included: an average signal counts every day with entries
    span = _dates(period.start_local, period.end_local)
    return {
        'total': _sum(days),
        'daily_average': _daily_average(days, span, signal, first_day, today),
        'average': _entry_mean(days),
        'count': sum(c for _, c in days.values()),
    }


def _dates(start: date, end: date) -> list[date]:
    """Days from start (inclusive) to end (exclusive)."""
    return [start + timedelta(days=i) for i in range((end - start).days)]


def _step_value(days: dict, span: list[date], signal: Signal, calculation: str,
                first_day: date | None, today: date) -> float | None:
    if calculation == WidgetCalculation.DAILY_AVERAGE:
        return _daily_average(days, span, signal, first_day, today)
    found = {day: days[day] for day in span if day in days}
    if calculation == WidgetCalculation.AVERAGE:
        return _entry_mean(found)
    if found:
        return _sum(found)
    tracked = first_day is not None and span[-1] >= first_day and span[0] <= today
    return 0.0 if tracked else None


def _is_partial(value: float | None, span: list[date], length: int, signal: Signal,
                calculation: str, first_day: date | None, today: date) -> bool:
    if value is None:
        return False
    if calculation == WidgetCalculation.TOTAL:
        return (
            len(span) < length
            or span[0] <= today <= span[-1]
            or (first_day is not None and span[0] < first_day <= span[-1])
        )
    return (
        calculation == WidgetCalculation.DAILY_AVERAGE
        and signal.counts_empty_days_as_zero
        and today in span
        and not any(_tracked(day, first_day, today) for day in span)
    )


def _trend_value(days: dict, start: date, length: int, window: int, signal: Signal,
                 calculation: str, first_day: date | None, today: date) -> float | None:
    """
    Moving average at the step of `length` days.
    """
    if start > today:
        return None
    starts = [start - timedelta(days=length * i) for i in range(window)]
    spans = [_dates(s, s + timedelta(days=length)) for s in starts]
    in_window = [day for span in spans for day in span]
    if calculation == WidgetCalculation.AVERAGE:
        return _entry_mean({day: days[day] for day in in_window if day in days})
    is_daily_average = calculation == WidgetCalculation.DAILY_AVERAGE
    if is_daily_average and not signal.counts_empty_days_as_zero:
        return _daily_average(days, in_window, signal, first_day, today)

    if spans[0][-1] >= today:
        return None
    if is_daily_average:
        tracked = [day for day in in_window if _tracked(day, first_day, today)]
        return _daily_average(days, tracked, signal, first_day, today) if tracked else None

    def is_complete(span):
        return first_day is not None and span[0] >= first_day and span[-1] < today

    totals = [sum(days[day][0] for day in span if day in days) for span in spans if is_complete(span)]
    return sum(totals) / len(totals) if totals else None


def _timeseries(rows, signal: Signal, calculation: str, period: Period, first_day: date | None,
                today: date) -> dict:
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
        value = _step_value(days, span, signal, calculation, first_day, today)
        points.append({
            'start': span[0].isoformat(),
            'end': span[-1].isoformat(),
            'value': value,
            'trend': _trend_value(
                days, step_start, length, TREND_WINDOW[step], signal, calculation, first_day, today),
            'partial': _is_partial(value, span, length, signal, calculation, first_day, today),
        })
    return {'step': step, 'points': points}


def _binned(rows, key) -> dict:
    """{key(day, hour): {day: [sum, entry count]}}, only for bins with entries."""
    bins = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    for day, hour, total, count in rows:
        b = bins[key(day, hour)][day]
        b[0] += total
        b[1] += count
    return bins


def _day_of_week(rows, signal: Signal, calculation: str, period: Period, first_day: date | None,
                 today: date) -> list[dict]:
    by_dow = _binned(rows, lambda day, hour: day.weekday())
    dates = _dates(period.start_local, period.end_local)

    def value(dow: int) -> float | None:
        days = by_dow.get(dow, {})
        if calculation == WidgetCalculation.TOTAL:
            return _sum(days)
        if calculation == WidgetCalculation.AVERAGE:
            return _entry_mean(days)
        span = [day for day in dates if day.weekday() == dow]
        return _daily_average(days, span, signal, first_day, today)

    return [{'dow': dow, 'value': value(dow)} for dow in range(7)]


def _heatmap(rows, signal: Signal, calculation: str) -> list[dict]:
    if calculation == WidgetCalculation.AVERAGE:
        value = _entry_mean
    elif (calculation == WidgetCalculation.DAILY_AVERAGE
          and signal.summary_method == SummaryMethod.AVERAGE):
        value = _mean_of_daily_means
    else:
        value = _sum
    return [
        {'dow': dow, 'hour': hour, 'count': sum(c for _, c in days.values()), 'value': value(days)}
        for (dow, hour), days in _binned(rows, lambda day, hour: (day.weekday(), hour)).items()
    ]
