from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from rest_framework.test import APIClient

from apps.events.models import Event, SignalEntry
from apps.signals.models import Signal, SignalType, SummaryMethod

from .calculations import available_calculations, default_calculation
from .models import AnalyticsBoard, AnalyticsWidget, WidgetCalculation, WidgetTimeframe
from .serializers import AnalyticsWidgetCreateSerializer
from .services import get_signal_stats, get_widget_values, resolve_period

TZ = ZoneInfo('UTC')
MONDAY = date(2026, 11, 2)
LATER = date(2026, 11, 30)  # every day of the example week is over


def make_signal(user, summary_method, signal_type=SignalType.VALUE):
    return Signal.objects.create(
        user=user, name='S', type=signal_type, summary_method=summary_method)


def log(user, signal, day, *values, hour=12):
    for value in values:
        when = datetime(day.year, day.month, day.day, hour, tzinfo=TZ)
        event = Event.objects.create(user=user, occurred_at=when)
        SignalEntry.objects.create(event=event, signal=signal, value=Decimal(value))


def example(user, signal):
    """Monday: 4 and 5. Tuesday: nothing. Wednesday: 3."""
    log(user, signal, MONDAY, 4, 5)
    log(user, signal, MONDAY + timedelta(days=2), 3)


def stats(user, signal, calculation, timeframe='week', start=MONDAY, today=LATER):
    period = resolve_period(timeframe, start, TZ)
    return get_signal_stats(signal, user, period, today, calculation)


def values(result):
    return [p['value'] for p in result['timeseries']['points']]


@pytest.mark.parametrize('signal_type', [SignalType.VALUE, SignalType.RANGE, SignalType.DURATION])
@pytest.mark.parametrize('summary_method', SummaryMethod.values)
def test_every_calculation_whatever_the_summary_method(user, signal_type, summary_method):
    signal = make_signal(user, summary_method, signal_type)
    assert available_calculations(signal) == WidgetCalculation.values


def test_tally_has_no_average_per_entry(user):
    signal = make_signal(user, SummaryMethod.SUM, SignalType.TALLY)
    assert available_calculations(signal) == ['total', 'daily_average']


@pytest.mark.parametrize('summary_method, expected', [
    (SummaryMethod.SUM, 'total'), (SummaryMethod.AVERAGE, 'daily_average'),
])
def test_summary_method_preselects(user, summary_method, expected):
    assert default_calculation(make_signal(user, summary_method)) == expected


@pytest.mark.parametrize('summary_method, daily_average', [
    (SummaryMethod.SUM, 12 / 7),             # all seven days since the first entry
    (SummaryMethod.AVERAGE, (4.5 + 3) / 2),  # only days with entries
])
def test_period_numbers(user, summary_method, daily_average):
    signal = make_signal(user, summary_method)
    example(user, signal)
    result = stats(user, signal, 'total')
    assert result['total'] == 12
    assert result['daily_average'] == pytest.approx(daily_average)
    assert result['average'] == 4


def test_period_daily_average_of_total_signal_in_the_example(user):
    signal = make_signal(user, SummaryMethod.SUM)
    example(user, signal)
    result = stats(user, signal, 'daily_average', today=MONDAY + timedelta(days=3))
    assert result['daily_average'] == 4  # (9 + 0 + 3) / 3


@pytest.mark.parametrize('summary_method, calculation, expected', [
    (SummaryMethod.SUM, 'total', [9, 0, 3]),
    (SummaryMethod.SUM, 'daily_average', [9, 0, 3]),
    (SummaryMethod.SUM, 'average', [4.5, None, 3]),
    (SummaryMethod.AVERAGE, 'total', [9, 0, 3]),
    (SummaryMethod.AVERAGE, 'daily_average', [4.5, None, 3]),
    (SummaryMethod.AVERAGE, 'average', [4.5, None, 3]),
])
def test_daily_steps(user, summary_method, calculation, expected):
    signal = make_signal(user, summary_method)
    example(user, signal)
    assert values(stats(user, signal, calculation))[:3] == expected


def test_weekly_daily_average_is_per_tracked_day(user):
    signal = make_signal(user, SummaryMethod.SUM)
    wednesday = date(2026, 11, 4)
    log(user, signal, wednesday, 10)  # tracking begins mid week
    log(user, signal, date(2026, 11, 10), 6)
    log(user, signal, date(2026, 11, 11), 100)  # today, unfinished
    result = stats(user, signal, 'daily_average', 'year', today=date(2026, 11, 11))
    points = {p['start']: p for p in result['timeseries']['points']}
    assert points['2026-11-02']['value'] == 2  # 10 over Wednesday to Sunday
    assert points['2026-11-09']['value'] == 3  # Monday and Tuesday
    assert points['2026-11-02']['partial'] is points['2026-11-09']['partial'] is False
    assert points['2026-11-02']['trend'] == 2
    assert points['2026-11-09']['trend'] is None  # unfinished
    assert points['2026-10-26']['value'] is None  # before the first entry


@pytest.mark.parametrize('logged, expected', [([5], 5), ([], 0)])
def test_daily_average_resting_only_on_today_is_partial(user, logged, expected):
    signal = make_signal(user, SummaryMethod.SUM)
    log(user, signal, MONDAY - timedelta(days=7), 1)
    log(user, signal, MONDAY, *logged)
    result = stats(user, signal, 'daily_average', today=MONDAY)
    first = result['timeseries']['points'][0]
    assert (first['value'], first['partial']) == (expected, True)
    assert result['daily_average'] == expected
    assert values(result)[1:] == [None] * 6  # the future


def test_daily_average_shows_future_entries(user):
    signal = make_signal(user, SummaryMethod.SUM)
    log(user, signal, MONDAY, 1)
    log(user, signal, MONDAY + timedelta(days=4), 7)
    result = stats(user, signal, 'daily_average', today=MONDAY)
    assert values(result)[4] == 7


@pytest.mark.parametrize('calculation, mondays', [
    ('total', 18), ('daily_average', 6), ('average', 3.6),
])
def test_day_of_week_of_total_signal(user, calculation, mondays):
    signal = make_signal(user, SummaryMethod.SUM)
    log(user, signal, MONDAY, 4, 5)
    log(user, signal, MONDAY + timedelta(days=14), 3, 3, 3)  # the Monday between is empty
    result = stats(user, signal, calculation, 'month', today=MONDAY + timedelta(days=15))
    assert result['day_of_week'][0]['value'] == mondays


@pytest.mark.parametrize('calculation, expected', [
    ('total', 9), ('daily_average', 9), ('average', 4.5),
])
def test_heatmap_of_total_signal(user, calculation, expected):
    signal = make_signal(user, SummaryMethod.SUM)
    log(user, signal, MONDAY, 4, 5)
    assert stats(user, signal, calculation)['heatmap'][0]['value'] == expected


def test_changing_the_summary_method_keeps_the_stored_calculation(user):
    signal = make_signal(user, SummaryMethod.SUM)
    today = datetime.now(TZ).date()
    log(user, signal, today - timedelta(days=1), 2, 4)
    board = AnalyticsBoard.objects.create(user=user, name='B')
    widget = AnalyticsWidget.objects.create(
        board=board, signal=signal, config={'calculation': 'daily_average'},
        timeframe=WidgetTimeframe.LAST_DAYS, days=2)
    assert get_widget_values(widget, user, TZ)['value'] == 6
    signal.summary_method = SummaryMethod.AVERAGE
    signal.save()
    widget.refresh_from_db()
    assert widget.config['calculation'] == 'daily_average'
    assert get_widget_values(widget, user, TZ)['value'] == 3


def test_stored_calculation_a_tally_lacks_falls_back_to_the_default(user):
    signal = make_signal(user, SummaryMethod.SUM, SignalType.TALLY)
    today = datetime.now(TZ).date()
    log(user, signal, today, 1, 1)
    board = AnalyticsBoard.objects.create(user=user, name='B')
    widget = AnalyticsWidget.objects.create(
        board=board, signal=signal, config={'calculation': 'average'},
        timeframe=WidgetTimeframe.TODAY)
    assert get_widget_values(widget, user, TZ)['value'] == 2


@pytest.mark.parametrize('widget_type', ['value', 'timeseries'])
@pytest.mark.parametrize('signal_type, calculation, valid', [
    (SignalType.VALUE, 'total', True),
    (SignalType.VALUE, 'daily_average', True),
    (SignalType.VALUE, 'average', True),
    (SignalType.TALLY, 'total', True),
    (SignalType.TALLY, 'daily_average', True),
    (SignalType.TALLY, 'average', False),
])
def test_calculations_a_widget_accepts(user, rf, widget_type, signal_type, calculation, valid):
    signal = make_signal(user, SummaryMethod.SUM, signal_type)
    board = AnalyticsBoard.objects.create(user=user, name='B')
    request = rf.post('/')
    request.user = user
    serializer = AnalyticsWidgetCreateSerializer(context={'request': request}, data={
        'board_id': board.id, 'signal_id': signal.id, 'type': widget_type, 'title': 'W',
        'config': {'calculation': calculation}, 'timeframe': 'this_week',
    })
    assert serializer.is_valid() == valid


def test_stats_endpoint(user):
    client = APIClient()
    client.force_authenticate(user)
    tally = make_signal(user, SummaryMethod.SUM, SignalType.TALLY)
    url = f'/api/analytics/signals/{tally.id}/stats/?timeframe=week&period_start=2026-11-02&tz=UTC'
    assert client.get(url).data['calculation'] == 'total'
    assert client.get(url + '&calculation=daily_average').data['calculation'] == 'daily_average'
    assert client.get(url + '&calculation=average').status_code == 400
    assert client.get(url + '&calculation=median').status_code == 400


def zero_signal(user):
    return Signal.objects.create(
        user=user, name='Sad', type=SignalType.VALUE, summary_method=SummaryMethod.AVERAGE,
        empty_days_as_zero=True)


def test_counting_empty_days_averages_each_day_first(user):
    signal = zero_signal(user)
    log(user, signal, MONDAY, 2, 4)  # a day of 3
    log(user, signal, MONDAY + timedelta(days=4), 4)
    result = stats(user, signal, 'daily_average')
    assert result['daily_average'] == 1  # (3 + 4) / 7
    assert values(result) == [3, 0, 0, 0, 4, 0, 0]
    assert result['average'] == pytest.approx(10 / 3)  # no entries are made up
    assert result['total'] == 10
    assert [d['value'] for d in result['day_of_week']] == [3, 0, 0, 0, 4, 0, 0]
    assert sorted(c['value'] for c in result['heatmap']) == [3, 4]
    # the week after: nothing logged, but every day counts
    later = stats(user, signal, 'daily_average', start=MONDAY + timedelta(days=7))
    assert later['daily_average'] == 0 and values(later) == [0] * 7
    assert later['average'] is None
    assert later['timeseries']['points'][0]['trend'] == pytest.approx(4 / 7)  # Tue 3 to Mon 9
    # before the first entry there is nothing
    earlier = stats(user, signal, 'daily_average', start=MONDAY - timedelta(days=7))
    assert earlier['daily_average'] is None and values(earlier) == [None] * 7


def test_counting_empty_days_leaves_out_the_unfinished_today(user):
    signal = zero_signal(user)
    log(user, signal, MONDAY, 4)
    result = stats(user, signal, 'daily_average', today=MONDAY + timedelta(days=2))
    assert result['daily_average'] == 2  # Monday and an empty Tuesday
    today = result['timeseries']['points'][2]
    assert (today['value'], today['partial'], today['trend']) == (0, True, None)


@pytest.mark.parametrize('calculation, expected', [
    ('daily_average', 0), ('average', None), ('total', 0),
])
def test_value_widget_of_a_period_without_entries(user, calculation, expected):
    signal = zero_signal(user)
    today = datetime.now(TZ).date()
    log(user, signal, today - timedelta(days=30), 5)
    board = AnalyticsBoard.objects.create(user=user, name='B')
    widget = AnalyticsWidget.objects.create(
        board=board, signal=signal, config={'calculation': calculation},
        timeframe=WidgetTimeframe.LAST_DAYS, days=7)
    result = get_widget_values(widget, user, TZ)
    assert (result['value'], result['count']) == (expected, 0)


def api_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_api_keeps_the_option_for_average_signals_only(user):
    api = api_for(user)

    def create(**fields):
        payload = {'name': 'S', 'summary_method': 'average', 'empty_days_as_zero': True, **fields}
        response = api.post('/api/signals/', payload, format='json')
        assert response.status_code == 201, response.data
        return response.data

    assert create(type='value', value_config={'unit': 'x'})['empty_days_as_zero'] is True
    assert create(type='duration')['empty_days_as_zero'] is True
    for minimum in (0, 1, -5):
        scale = {'min_value': minimum, 'max_value': 5}
        rated = create(type='range', range_config=scale)
        assert rated['empty_days_as_zero'] is True
    assert create(type='duration', summary_method='total')['empty_days_as_zero'] is False
    assert create(type='tally')['empty_days_as_zero'] is False

    url = f'/api/signals/{rated["id"]}/'
    assert api.patch(url, {'name': 'T'}, format='json').data['empty_days_as_zero'] is True
    changed = api.patch(url, {'summary_method': 'total'}, format='json')
    assert changed.data['empty_days_as_zero'] is False
