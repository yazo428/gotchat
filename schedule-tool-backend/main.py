from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from resolve_datetime import resolve_datetime

app = FastAPI()

# CORS設定
# TODO: allow_originsにViteのdevサーバーのオリジンを入れる
#       （`npm run dev`実行時にターミナルに表示されるURLを確認。デフォルトは5173系のことが多い）
app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
  ],
  allow_methods=["POST"],
  allow_headers=["*"],
)


class ResolveRequest(BaseModel):
  text: str


class DateTimeRange(BaseModel):
  start: str  # TODO: pendulum.DateTimeをどう文字列化するか下記コメント参照
  end: str


class ResolveResponse(BaseModel):
  results: list[DateTimeRange]


@app.post("/resolve", response_model=ResolveResponse)
def resolve(req: ResolveRequest) -> ResolveResponse:
  pairs = resolve_datetime(req.text)
  results = [DateTimeRange(start=s.isoformat(), end=e.isoformat()) for s, e in pairs]
  return ResolveResponse(results=results)