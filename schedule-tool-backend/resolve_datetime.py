import pendulum
from ja_timex import TimexParser
from str_to_list import str_to_list

DEFAULT_DURATION_HOUR = 1


def apply_fragment(base, t):
    if t.type == "DURATION":
        unit = t.value[-1]
        if t.mod == "AFTER":
          base += t.to_duration()
        elif t.mod == "BEFORE":
          base -= t.to_duration()
        if unit == "W" and base.weekday() != 0:
          base = base.previous(pendulum.MONDAY)
    elif t.type == "DATE":
      if t.value.startswith("XXXX-WXX-"):
        now_weekday = base.weekday()
        input_weekday = int(t.value.split("-")[-1])
        diff = input_weekday - now_weekday - 1
        base = base.add(days=diff)
      else:
        year_str, month_str, day_str = t.value.split("-")
        kwargs = {}
        if "X" not in year_str:
          kwargs["year"] = int(year_str)
        if "X" not in month_str:
          kwargs["month"] = int(month_str)
        if "X" not in day_str:
          kwargs["day"] = int(day_str)
        base = base.set(**kwargs)
    elif t.type == "TIME":
      hour_str, minute_str, second_str = t.value.split("-")
      kwargs = {}
      if "X" not in hour_str:
        kwargs["hour"] = int(hour_str[1:])
      if "X" not in minute_str:
        kwargs["minute"] = int(minute_str)
      if "X" not in second_str:
        kwargs["second"] = int(second_str)
      base = base.set(**kwargs)
    return base


def _resolve_single(text: str) -> tuple:
    now = pendulum.now()
    parser = TimexParser(reference=now)
    timexes = parser.parse(text)

    result = now.start_of("day")
    result_end = None

    for t in timexes:
        if (t.range_start or t.range_end) and result_end is None:
            result_end = result

        if t.range_end:
            result_end = apply_fragment(result_end, t)
        else:
            result = apply_fragment(result, t)
            if result_end is not None:
                result_end = apply_fragment(result_end, t)

    if result_end is None:
        result_end = result + pendulum.duration(hours=DEFAULT_DURATION_HOUR)

    return result, result_end


def resolve_datetime(text: str) -> list[tuple]:
    return [_resolve_single(item) for item in str_to_list(text)]
