from django import template

register = template.Library()

# Canonical Monday-first ordering. JSONB does not preserve the key order the
# schedule was saved with, so we always render days in this fixed sequence.
_WEEKDAYS = (
    ("monday", "Mon", "Monday"),
    ("tuesday", "Tue", "Tuesday"),
    ("wednesday", "Wed", "Wednesday"),
    ("thursday", "Thu", "Thursday"),
    ("friday", "Fri", "Friday"),
    ("saturday", "Sat", "Saturday"),
    ("sunday", "Sun", "Sunday"),
)


@register.filter
def weekday_pills(days_of_week):
    """Normalize a ``days_of_week`` dict into an ordered list for display.

    Returns a list of dicts ``{"abbr", "name", "active"}`` in Monday→Sunday
    order, regardless of the key order stored in the JSON field. Unknown or
    missing keys are treated as inactive.
    """
    data = days_of_week if isinstance(days_of_week, dict) else {}
    return [
        {"abbr": abbr, "name": name, "active": bool(data.get(key, False))}
        for key, abbr, name in _WEEKDAYS
    ]
