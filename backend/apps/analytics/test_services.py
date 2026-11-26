from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from apps.events.models import Event, SignalEntry
from apps.signals.models import Signal, SignalRangeConfig, SignalType, SummaryMethod

from .services import get_signal_stats, resolve_period

TZ = ZoneInfo('UTC')


def log(user, signal, when, value):
    event = Event.objects.create(user=user, occurred_at=when)
    SignalEntry.objects.create(event=event, signal=signal, value=Decimal(value))


@pytest.fixture
def signal(user):
    """Range signal with logs. Monday: 5. Tuesday: 1, 1, 1, 1. Wednesday: no logs."""
    signal = Signal.objects.create(
        user=user, name='Mood', type=SignalType.RANGE,
        summary_method=SummaryMethod.AVERAGE,
    )
    SignalRangeConfig.objects.create(signal=signal, min_value=1, max_value=5)
    logs = [(2, 8, 5)] + [(3, h, 1) for h in (8, 10, 12, 14)]
    for day, hour, value in logs:
        log(user, signal, datetime(2026, 11, day, hour, tzinfo=TZ), value)
    return signal


@pytest.fixture
def stats(signal, user):
    """Weekly stats (Mon 2 to Sun 8 Nov 2026) in the given calculation."""
    def _stats(calculation):
        period = resolve_period('week', date(2026, 11, 4), TZ)
        return get_signal_stats(signal, user, period, calculation=calculation)
    return _stats


def test_average_is_one_mean_over_all_entries(stats):
    result = stats('average')
    assert result['average'] == pytest.approx(1.8)
    assert result['count'] == 5


def test_daily_average_is_the_mean_of_daily_means(stats):
    result = stats('daily_average')
    assert result['daily_average'] == pytest.approx(3.0)
    assert result['count'] == 5  # still the number of entries


def by_start(result):
    return {p['start']: p for p in result['timeseries']['points']}


@pytest.mark.parametrize('calculation', ['daily_average', 'average'])
def test_days_without_logs_are_skipped(stats, calculation):
    series = by_start(stats(calculation))
    assert series['2026-11-04']['value'] is None
    assert series['2026-11-08']['value'] is None


def test_daily_steps_of_both_averages_are_the_same(stats):
    entry = [p['value'] for p in by_start(stats('average')).values()]
    daily = [p['value'] for p in by_start(stats('daily_average')).values()]
    assert entry == daily


def test_day_of_week_and_heatmap_follow_the_calculation(stats):
    result = stats('daily_average')
    assert {d['dow']: d['value'] for d in result['day_of_week']}[1] == 1.0
    cells = {(c['dow'], c['hour']): c for c in result['heatmap']}
    assert cells[(0, 8)]['value'] == 5.0


@pytest.mark.parametrize('calculation, expected', [
    ('daily_average', 2.0),  # (1 + 3) / 2
    ('average', 1.4),        # (1 + 1 + 1 + 1 + 3) / 5
])
def test_two_weeks_of_same_weekday(user, signal, calculation, expected):
    # a second Tuesday (the 10th) with a single log of 3
    log(user, signal, datetime(2026, 11, 10, 9, tzinfo=TZ), 3)
    period = resolve_period('month', date(2026, 11, 1), TZ)
    result = get_signal_stats(signal, user, period, calculation=calculation)
    assert {d['dow']: d['value'] for d in result['day_of_week']}[1] == pytest.approx(expected)
