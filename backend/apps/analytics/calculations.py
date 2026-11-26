"""
Which calculations a signal offers.
"""

from apps.signals.models import Signal, SignalType, SummaryMethod

from .choices import WidgetCalculation


def available_calculations(signal: Signal) -> list[str]:
    if signal.type == SignalType.TALLY:
        return [WidgetCalculation.TOTAL.value, WidgetCalculation.DAILY_AVERAGE.value]
    return list(WidgetCalculation.values)


def default_calculation(signal: Signal) -> str:
    if signal.summary_method == SummaryMethod.AVERAGE:
        return WidgetCalculation.DAILY_AVERAGE.value
    return WidgetCalculation.TOTAL.value


def supported_calculation(signal: Signal, calculation: str) -> str:
    if calculation in available_calculations(signal):
        return calculation
    return default_calculation(signal)
