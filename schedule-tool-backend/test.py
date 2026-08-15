from ja_timex import TimexParser

parser = TimexParser()
timexes = parser.parse("火曜日と水曜日の午後5時から19時まで")
print([t.text for t in timexes])
print([t.span for t in timexes])