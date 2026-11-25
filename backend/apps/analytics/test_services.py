from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from apps.events.models import Event, SignalEntry
from apps.signals.models import AverageWeighting, Signal, SignalRangeConfig, SignalType, SummaryMethod

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
    """Weekly stats (Mon 2 to Sun 8 Nov 2026) for the given weighting."""
    def _stats(weighting):
        signal.average_weighting = weighting
        period = resolve_period('week', date(2026, 11, 4), TZ)
        return get_signal_stats(signal, user, period)
    return _stats


def test_default_weighting_is_log():
    assert Signal._meta.get_field('average_weighting').default == AverageWeighting.EVENT


def test_log_weighting_is_one_mean_over_all_logs(stats):
    result = stats(AverageWeighting.EVENT)
    assert result['average'] == pytest.approx(1.8)
    assert result['count'] == 5


def test_day_weighting_is_mean_of_daily_means(stats):
    result = stats(AverageWeighting.DAY)
    assert result['average'] == pytest.approx(3.0)
    assert result['count'] == 5  # still the number of logs


def by_start(result):
    return {p['start']: p for p in result['timeseries']['points']}


@pytest.mark.parametrize('weighting', AverageWeighting.values)
def test_days_without_logs_are_skipped(stats, weighting):
    series = by_start(stats(weighting))
    assert series['2026-11-04']['value'] is None
    assert series['2026-11-08']['value'] is None


def test_daily_values_are_the_same_in_both_modes(stats):
    log_values = [p['value'] for p in by_start(stats(AverageWeighting.EVENT)).values()]
    day_values = [p['value'] for p in by_start(stats(AverageWeighting.DAY)).values()]
    assert log_values == day_values


def test_day_of_week_and_heatmap_follow_the_weighting(stats):
    result = stats(AverageWeighting.DAY)
    assert {d['dow']: d['value'] for d in result['day_of_week']}[1] == 1.0
    cells = {(c['dow'], c['hour']): c for c in result['heatmap']}
    assert cells[(0, 8)]['value'] == 5.0


@pytest.mark.parametrize('weighting, expected', [
    (AverageWeighting.DAY, 2.0),    # (1 + 3) / 2
    (AverageWeighting.EVENT, 1.4),  # (1 + 1 + 1 + 1 + 3) / 5
])
def test_two_weeks_of_same_weekday(user, signal, weighting, expected):
    # a second Tuesday (the 10th) with a single log of 3
    log(user, signal, datetime(2026, 11, 10, 9, tzinfo=TZ), 3)
    signal.average_weighting = weighting
    period = resolve_period('month', date(2026, 11, 1), TZ)
    dow = {d['dow']: d['value'] for d in get_signal_stats(signal, user, period)['day_of_week']}
    assert dow[1] == pytest.approx(expected)
