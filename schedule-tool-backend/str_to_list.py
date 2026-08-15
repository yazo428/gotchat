from ja_timex import TimexParser
import MeCab

# 列挙の区切りとみなす表層形
COORDINATING_TOKENS = {"と", "や", "とか", "・", "、",","}

# ja_timex が単体では DATE として認識しない略称曜日
WEEKDAY_ABBR = {"月", "火", "水", "木", "金", "土", "日"}


def _find_timex_spans(text: str) -> list[tuple[int, int]]:
    parser = TimexParser()
    timexes = parser.parse(text)
    return [t.span for t in timexes]


def _is_inside_any_span(pos_start: int, pos_end: int, spans: list[tuple[int, int]]) -> bool:
    for start, end in spans:
        if start <= pos_start and pos_end <= end:
            return True
    return False


def _find_split_positions(text: str, spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    tagger = MeCab.Tagger("-r /opt/homebrew/etc/mecabrc")
    node = tagger.parseToNode(text)

    split_positions: list[tuple[int, int]] = []
    pos = 0  # 現在のノードの開始文字位置

    while node:
        surface = node.surface
        if surface:
            if surface in COORDINATING_TOKENS:
                token_start, token_end = pos, pos + len(surface)
                if not _is_inside_any_span(token_start, token_end, spans):
                    split_positions.append((token_start, token_end))
        pos += len(surface)
        node = node.next

    return split_positions


def _normalize_weekday_abbr(chunks: list[str]) -> list[str]:
    """略称曜日（月/火/水/木/金/土/日）に「曜」を補い、ja_timex が認識できる正式形にする。

    チャンク内の全文字を走査し、WEEKDAY_ABBR に含まれ、TIMEXスパンで覆われておらず、
    直後がすでに「曜」でない文字に「曜」を挿入する。
    「今日」「1月」のように TIMEX として認識済みの文字には補完しない。

    例: "来週の月" -> "来週の月曜", "水の15時" -> "水曜の15時", "今日" -> "今日"（変化なし）
    """
    parser = TimexParser()
    result = []
    for chunk in chunks:
        timexes = parser.parse(chunk)
        covered_positions = set()
        for t in timexes:
            covered_positions.update(range(t.span[0], t.span[1]))

        normalized = []
        for i, ch in enumerate(chunk):
            normalized.append(ch)
            next_ch = chunk[i + 1] if i + 1 < len(chunk) else ""
            if ch in WEEKDAY_ABBR and i not in covered_positions and next_ch != "曜":
                normalized.append("曜")
        result.append("".join(normalized))
    return result


def _propagate_prefix(chunks: list[str]) -> list[str]:
    """先頭チャンクの週修飾子（来週など）を、裸の曜日チャンクへ補完する。

    例: ["来週の水曜", "木曜"] -> ["来週の水曜", "来週の木曜"]
    """
    if len(chunks) <= 1:
        return chunks

    parser = TimexParser()
    first_timexes = parser.parse(chunks[0])

    # 先頭チャンクに週修飾子（DURATION / value に "W" を含む）がなければ何もしない
    has_week_mod = any(t.type == "DURATION" and "W" in t.value for t in first_timexes)
    if not has_week_mod:
        return chunks

    # プレフィックス境界を決定する
    # 正式な曜日表現（月曜など）: 最初の DATE timex の開始位置
    # 略称曜日（月・水など）: DURATION 終端 + "の"（ja_timex が DATE を返さないため）
    date_timexes = [t for t in first_timexes if t.type == "DATE"]
    if date_timexes:
        boundary = date_timexes[0].span[0]
    else:
        week_mod = next(t for t in first_timexes if t.type == "DURATION" and "W" in t.value)
        boundary = week_mod.span[1]
        if boundary < len(chunks[0]) and chunks[0][boundary] == "の":
            boundary += 1

    prefix = chunks[0][:boundary]
    if not prefix:
        return chunks

    result = [chunks[0]]
    for chunk in chunks[1:]:
        chunk_timexes = parser.parse(chunk)
        # XXXX-WXX-N（週コンテキストなしの正式曜日）または略称曜日で始まるチャンク
        is_bare_weekday = (
            any(t.type == "DATE" and t.value.startswith("XXXX-WXX-") for t in chunk_timexes)
            or chunk in WEEKDAY_ABBR
            or (chunk and chunk[0] in WEEKDAY_ABBR and not chunk_timexes)
        )
        result.append(prefix + chunk if is_bare_weekday else chunk)
    return result


def _propagate_suffix(chunks: list[str]) -> list[str]:
    """最後のチャンクの先頭TIMEX以降のサフィックスを、TIME timexを持たない先行チャンクへ補完する。

    例: ["月曜", "水曜", "金曜の15時"] -> ["月曜の15時", "水曜の15時", "金曜の15時"]
    """
    if len(chunks) <= 1:
        return chunks

    parser = TimexParser()
    last = chunks[-1]
    last_timexes = parser.parse(last)

    if not last_timexes:
        return chunks

    # TIME以外の最後のTIMEXの終端を境界とし、そこ以降をサフィックスとする
    # （先頭TIMEXを使うと "来週の木曜" の "の木曜" が誤って伝播してしまう）
    non_time = [t for t in last_timexes if t.type != "TIME"]
    if not non_time:
        return chunks
    suffix = last[non_time[-1].span[1]:]
    if not suffix:
        return chunks

    result = []
    for chunk in chunks[:-1]:
        has_time = any(t.type == "TIME" for t in parser.parse(chunk))
        result.append(chunk if has_time else chunk + suffix)
    result.append(last)
    return result


def str_to_list(text: str) -> list[str]:
    spans = _find_timex_spans(text)
    split_positions = _find_split_positions(text, spans)

    result: list[str] = []
    prev_end = 0
    for start, end in sorted(split_positions):
        chunk = text[prev_end:start]
        if chunk:
            result.append(chunk)
        prev_end = end
    tail = text[prev_end:]
    if tail:
        result.append(tail)
    result = _normalize_weekday_abbr(result)
    result = _propagate_prefix(result)
    return _propagate_suffix(result)

if __name__ == "__main__":
    test_cases = [
        "月曜・水曜・金曜の15時",
        "月曜の10時と水曜の15時",
        "来週の月、水・金曜の15時から17時",
        "来週の水曜日と木曜日"
    ]
    for text in test_cases:
        print(text, "->", str_to_list(text))