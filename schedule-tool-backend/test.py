import pendulum
from ja_timex import TimexParser

def resolve_datetime(text: str) -> pendulum.DateTime:
  now = pendulum.now()
  parser = TimexParser(reference = now)
  timexes = parser.parse(text)

  result = now.start_of("day")
  print(result)
  print("------------------------------------------")
  for t in timexes:
    print(t)
    if t.type == "DURATION":
      unit = t.value[-1]
      if t.mod == "AFTER":
        result += t.to_duration()
      elif t.mod == "BEFORE":
        result -= t.to_duration()
      if unit == "W":
        if result.weekday() != 0:
          result = result.previous(pendulum.MONDAY)
    elif t.type == "DATE":
      if t.value.startswith("XXXX-WXX-"):#曜日の指定の場合
        now_weekday = result.weekday()
        input_weekday = int(t.value.split("-")[-1])
        diff = input_weekday - now_weekday -1
        result = result.add(days=diff)
      else:#年月日の場合、入力された値に置き換える
        year_str, month_str, day_str = t.value.split("-")
        kwargs = {}
        if "X" not in year_str:
          kwargs["year"] = int(year_str)
        if "X" not in month_str:
          kwargs["month"] = int(month_str)
        if "X" not in day_str:
          kwargs["day"] = int(day_str)
        result = result.set(**kwargs)
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
      result = result.set(**kwargs)

    print(result)
  return result
if __name__ == "__main__":
  answer = resolve_datetime("来週の日曜の午後3時から")
  print("結果",answer)
  print("------------------------------------------")
  answer = resolve_datetime("明日の4時から6時まで")
  print("結果",answer)