from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from apps.events.models import Event, SignalEntry
from apps.signals.models import AverageWeighting, Signal, SignalType, SummaryMethod

from .models import AnalyticsBoard, AnalyticsWidget, WidgetAggregation, WidgetTimeframe
from .serializers import AnalyticsWidgetCreateSerializer
from .services import get_signal_stats, get_widget_values, resolve_period

TZ = ZoneInfo('UTC')
TODAY = date(2026, 11, 11)  # a Wednesday


def log(user, signal, day, value=1, hour=12):
    when = datetime(day.year, day.month, day.day, hour, tzinfo=TZ)
    event = Event.objects.create(user=user, occurred_at=when)
    SignalEntry.objects.create(event=event, signal=signal, value=Decimal(value))


def nov(day):
    return date(2026, 11, day)


def make_signal(user, summary_method, **kwargs):
    # type VALUE needs no config row for the services
    return Signal.objects.create(
        user=user, name='S', type=SignalType.VALUE, summary_method=summary_method, **kwargs)


@pytest.fixture
def total(user):
    return make_signal(user, SummaryMethod.SUM)


@pytest.fixture
def average(user):
    return make_signal(user, SummaryMethod.AVERAGE)


def stats(signal, user, timeframe='week', start=TODAY, today=TODAY):
    return get_signal_stats(signal, user, resolve_period(timeframe, start, TZ), today)


def column(result, key):
    return [p[key] for p in result['timeseries']['points']]


def test_future_days_are_empty(user, total):
    log(user, total, nov(9), 2)
    result = stats(total, user)
    assert column(result, 'value') == [2, 0, 0, None, None, None, None]
    assert column(result, 'trend')[3:] == [None] * 4


def test_future_entries_are_still_shown(user, total):
    log(user, total, nov(13), 4)
    assert column(stats(total, user), 'value')[4] == 4


def test_days_before_the_first_entry_are_empty(user, total):
    log(user, total, nov(10), 2)
    assert column(stats(total, user), 'value')[:3] == [None, 2, 0]


def test_signal_without_entries_has_no_values(user, total):
    result = stats(total, user)
    assert column(result, 'value') == [None] * 7
    assert column(result, 'trend') == [None] * 7
    assert result['average'] == 0


def test_only_today_is_partial_in_daily_steps(user, total):
    log(user, total, nov(1))
    assert column(stats(total, user), 'partial') == [False, False, True] + [False] * 4


def test_trend_uses_the_days_before_the_period(user, total):
    for day in range(3, 9):  # Tue 3 to Sun 8, before the shown week
        log(user, total, nov(day), 7)
    # Monday 9: six days of 7 and an empty Monday
    assert column(stats(total, user), 'trend')[0] == pytest.approx(6)


def test_trend_leaves_out_today(user, total):
    for day in range(1, 12):
        log(user, total, nov(day), 1 if day < 11 else 100)
    trend = column(stats(total, user), 'trend')
    assert trend[1] == 1
    assert trend[2] is None


def test_trend_of_total_signal_starts_at_the_first_entry(user, total):
    log(user, total, nov(3), 6)
    result = stats(total, user, start=nov(2), today=nov(30))
    assert column(result, 'trend')[:4] == [None, 6, 3, 2]


def test_trend_of_average_signal_has_no_minimum(user, average):
    for day, value in [(3, 2), (5, 4), (7, 6)]:
        log(user, average, nov(day), value)
    result = stats(average, user, start=nov(2), today=nov(30))
    assert column(result, 'trend') == [None, 2, 2, 3, 3, 4, 4]


@pytest.mark.parametrize('weighting, expected', [
    (AverageWeighting.EVENT, 2.2), (AverageWeighting.DAY, 3.0),
])
def test_trend_of_average_signal_follows_the_weighting(user, weighting, expected):
    signal = make_signal(user, SummaryMethod.AVERAGE, average_weighting=weighting)
    log(user, signal, nov(2), 5)
    for hour in (8, 9, 10):
        log(user, signal, nov(3), 1, hour)
    log(user, signal, nov(4), 3)
    result = stats(signal, user, start=nov(2), today=nov(30))
    assert column(result, 'trend')[2] == pytest.approx(expected)


def test_average_of_total_signal_is_per_completed_day(user, total):
    log(user, total, nov(1))
    log(user, total, nov(9), 6)
    log(user, total, nov(11), 100)  # today, unfinished
    result = stats(total, user)
    assert result['average'] == 3  # (6 + 0) / Monday and Tuesday
    assert result['total'] == 106


def test_average_of_total_signal_starts_at_the_first_entry(user, total):
    log(user, total, nov(10), 6)
    assert stats(total, user)['average'] == 6


def test_average_of_total_signal_with_only_today(user, total):
    log(user, total, TODAY, 5)
    assert stats(total, user)['average'] == 5


def test_year_uses_weekly_steps_clipped_to_the_period(user, total):
    log(user, total, date(2025, 12, 1))
    points = stats(total, user, 'year', today=date(2027, 3, 1))['timeseries']
    assert points['step'] == 'week'
    first, last = points['points'][0], points['points'][-1]
    assert (first['start'], first['end'], first['partial']) == ('2026-01-01', '2026-01-04', True)
    assert (last['start'], last['end'], last['partial']) == ('2026-12-28', '2026-12-31', True)


def test_weekly_trend_uses_full_weeks_before_the_period(user, total):
    # 7 per week: one entry every day from Mon 1 Dec 2025 to Sun 4 Jan 2026
    for i in range(35):
        log(user, total, date(2025, 12, 1) + timedelta(days=i))
    result = stats(total, user, 'year', today=date(2027, 3, 1))
    assert column(result, 'value')[0] == 4  # clipped to 1-4 January
    assert column(result, 'trend')[0] == 7


def test_unfinished_and_future_weeks(user, total):
    log(user, total, date(2026, 1, 1))
    result = stats(total, user, 'year')
    points = {p['start']: p for p in result['timeseries']['points']}
    assert points['2026-11-09']['partial'] is True
    assert points['2026-11-09']['trend'] is None
    assert points['2026-11-16']['value'] is None


def test_week_in_which_tracking_began_is_partial_and_not_in_the_trend(user, total):
    log(user, total, nov(4), 5)
    result = stats(total, user, 'year', today=date(2027, 3, 1))
    points = {p['start']: p for p in result['timeseries']['points']}
    assert points['2026-11-02']['partial'] is True
    assert points['2026-11-02']['trend'] is None  # no complete week yet
    assert points['2026-11-09']['trend'] == 0  # the week of the entry doesn't count


def test_tally_is_always_summed(user):
    signal = Signal.objects.create(
        user=user, name='Coffee', type=SignalType.TALLY, summary_method=SummaryMethod.AVERAGE)
    assert signal.summary_method == SummaryMethod.SUM


@pytest.mark.parametrize('aggregation, expected', [
    (WidgetAggregation.TOTAL, 9), (WidgetAggregation.AVERAGE, 4.5), (WidgetAggregation.PER_EVENT, 3),
])
def test_widget_value_of_total_signal(user, total, aggregation, expected):
    today = datetime.now(TZ).date()
    yesterday = today - timedelta(days=1)
    log(user, total, today - timedelta(days=2), 2)
    log(user, total, yesterday, 3)
    log(user, total, yesterday, 4)
    board = AnalyticsBoard.objects.create(user=user, name='B')
    widget = AnalyticsWidget.objects.create(
        board=board, signal=total, config={'aggregation': aggregation},
        timeframe=WidgetTimeframe.LAST_DAYS, days=3,
    )
    assert get_widget_values(widget, user, TZ)['value'] == pytest.approx(expected)


@pytest.mark.parametrize('signal_type, summary_method, expected', [
    (SignalType.VALUE, SummaryMethod.SUM, WidgetAggregation.PER_EVENT),
    (SignalType.VALUE, SummaryMethod.AVERAGE, WidgetAggregation.AVERAGE),
    (SignalType.TALLY, SummaryMethod.SUM, None),  # rejected
])
def test_per_event_is_only_kept_for_total_signals_with_values(
    user, rf, signal_type, summary_method, expected,
):
    signal = Signal.objects.create(
        user=user, name='S', type=signal_type, summary_method=summary_method)
    board = AnalyticsBoard.objects.create(user=user, name='B')
    request = rf.post('/')
    request.user = user
    serializer = AnalyticsWidgetCreateSerializer(context={'request': request}, data={
        'board_id': board.id, 'signal_id': signal.id, 'type': 'value', 'title': 'W',
        'config': {'aggregation': 'per_event'}, 'timeframe': 'this_week',
    })
    assert serializer.is_valid() == (expected is not None)
    if expected is not None:
        assert serializer.validated_data['config'] == {'aggregation': expected}
