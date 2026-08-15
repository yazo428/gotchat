# resolve_datetime.py

日本語の自然言語テキストを解析し、日時範囲のリストに変換するモジュール。
内部で `str_to_list` を使ってテキストを分割し、各要素を `(開始, 終了)` ペアに解決する。

---

## apply_fragment

```python
apply_fragment(base: pendulum.DateTime, t: Timex) -> pendulum.DateTime
```

`base` に timex オブジェクト `t` の情報を適用して、更新された日時を返す。

### 引数

| 引数 | 型 | 説明 |
|------|----|------|
| `base` | pendulum.DateTime | 変更対象の日時 |
| `t` | Timex | ja_timex がパースした時間表現オブジェクト |

### 戻り値

適用後の `pendulum.DateTime`。

### 動作（t.type 別）

**DURATION**
- `t.mod == "AFTER"` のとき `base += t.to_duration()`（〜後）
- `t.mod == "BEFORE"` のとき `base -= t.to_duration()`（〜前）
- 単位が `"W"`（週）かつ base が月曜でなければ、直前の月曜日に戻す
  - これをしないと「来週の金曜」→「一週間後」→次の金曜を探すと再来週になってしまう

**DATE**
- `t.value` が `XXXX-WXX-N` 形式（曜日指定）のとき
  - 現在曜日との差分を計算して `base` をその曜日に移動する
  - `diff = input_weekday - now_weekday - 1`（1-indexed → 0-indexed 変換）
- それ以外（年月日指定）のとき
  - `"X"` でない部分（year / month / day）だけを `base.set()` で上書きする

**TIME**
- `"X"` でない部分（hour / minute / second）だけを `base.set()` で上書きする

---

## _resolve_single

```python
_resolve_single(text: str) -> tuple[pendulum.DateTime, pendulum.DateTime]
```

単一の日時表現テキストを `(開始, 終了)` ペアに解決する。`resolve_datetime` の内部実装。

### 動作フロー

1. `pendulum.now()` で現在時刻を取得し、`TimexParser` で `text` をパースする
2. `result` を**今日の 0:00:00**、`result_end` を `None` で初期化する
3. パース結果の timex リストを順に処理する
   - `t.range_start` または `t.range_end` が立っていて `result_end` がまだ `None` なら、`result_end = result` で初期化する（range の終端基準を開始と同じ日に設定）
   - `t.range_end` が立っている → `result_end` に `apply_fragment` を適用
   - それ以外 → `result` に `apply_fragment` を適用し、`result_end` が存在する場合は `result_end` にも同じ fragment を適用（曜日や日付を両端に共有）
4. `result_end` が最終的に `None` のまま（範囲指定なし）なら、`result_end = result + 1時間`（`DEFAULT_DURATION_HOUR = 1`）とする
5. `(result, result_end)` を返す

---

## resolve_datetime

```python
resolve_datetime(text: str) -> list[tuple[pendulum.DateTime, pendulum.DateTime]]
```

日本語の自然言語テキストから、日時範囲 `(開始, 終了)` のリストを返す。

### 動作

1. `str_to_list(text)` でテキストを日時表現の単位に分割する
2. 各要素に `_resolve_single` を適用する
3. 結果のリストを返す

### 使用例

```python
resolve_datetime("月曜・水曜・金曜の15時")
# -> [
#     (DateTime(月曜 15:00), DateTime(月曜 16:00)),
#     (DateTime(水曜 15:00), DateTime(水曜 16:00)),
#     (DateTime(金曜 15:00), DateTime(金曜 16:00)),
# ]

resolve_datetime("来週の水曜と木曜の15時から17時")
# -> [
#     (DateTime(来週水曜 15:00), DateTime(来週水曜 17:00)),
#     (DateTime(来週木曜 15:00), DateTime(来週木曜 17:00)),
# ]

resolve_datetime("明日の4時から6時まで")
# -> [(DateTime(明日 04:00), DateTime(明日 06:00))]
```

---

## API エンドポイント（main.py）

`resolve_datetime` は FastAPI の `/resolve` エンドポイントから呼ばれる。

### リクエスト

```
POST /resolve
Content-Type: application/json
```

```json
{ "text": "月曜・水曜・金曜の15時" }
```

### レスポンス

```json
{
  "results": [
    { "start": "2026-08-10T15:00:00+09:00", "end": "2026-08-10T16:00:00+09:00" },
    { "start": "2026-08-12T15:00:00+09:00", "end": "2026-08-12T16:00:00+09:00" },
    { "start": "2026-08-14T15:00:00+09:00", "end": "2026-08-14T16:00:00+09:00" }
  ]
}
```

`start` / `end` は `pendulum.DateTime.isoformat()` によるISO8601形式（タイムゾーン付き）。
`results` は入力テキストを `str_to_list` で分割した要素数と同じ長さになる。
