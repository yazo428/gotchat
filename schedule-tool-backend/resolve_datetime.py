import pendulum
from ja_timex import TimexParser

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
      if t.value.startswith("XXXX-WXX-"):#曜日の指定の場合
        now_weekday = base.weekday()
        input_weekday = int(t.value.split("-")[-1])
        diff = input_weekday - now_weekday -1
        base = base.add(days=diff)
      else:#年月日の場合、入力された値に置き換える
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
        kwargs = {}
      if "X" not in hour_str:
        kwargs["hour"] = int(hour_str[1:])
      if "X" not in minute_str:
        kwargs["minute"] = int(minute_str)
      if "X" not in second_str:
        kwargs["second"] = int(second_str)
      base = base.set(**kwargs)
    return base


def resolve_datetime(text: str):
    now = pendulum.now()
    parser = TimexParser(reference=now)
    timexes = parser.parse(text)

    result = now.start_of("day")
    result_end = None

    # print(result)
    # print("------------------------------------------")
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
        # print(result)
        return result,result_end
    # print(result, result_end)
    return result, result_end

# if __name__ == "__main__":
#   answer = resolve_datetime("来週の日曜の午後3時から")
#   print("結果",answer)
#   print("------------------------------------------")
#   answer = resolve_datetime("明日の4時から6時まで")
#   print("結果",answer)