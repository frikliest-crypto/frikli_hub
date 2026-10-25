"""이번 주 추천을 골라 costco/index.html 정적 페이지로 만든다.

  python build.py --sample   샘플 데이터로 페이지만 생성 (API 키 불필요)
  python build.py            Claude로 아이템을 골라 페이지 생성
"""
import argparse
import json
import os
from datetime import date
from html import escape
from pathlib import Path

HERE = Path(__file__).parent


def render(items: list[dict], sample: bool) -> str:
    cards = "\n".join(
        f"""    <li>
      <h2>{i}. {escape(it['name'])}</h2>
      <p class="meta">{escape(it['category'])} · {escape(it['price_note'])}</p>
      <p>{escape(it['why'])}</p>
      <a href="{escape(it['source_url'], quote=True)}" rel="noopener">근거 보기</a>
    </li>"""
        for i, it in enumerate(items, 1)
    )
    banner = '<p class="sample">샘플 데이터예요. 실제 추천이 아니에요.</p>' if sample else ""
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>이번 주 코스트코 추천</title>
  <style>
    body {{ font-family: system-ui, "Malgun Gothic", sans-serif; max-width: 560px; margin: 0 auto; padding: 1rem; color: #222; word-break: keep-all; }}
    h1 {{ margin-bottom: .2rem; }}
    ol {{ list-style: none; padding: 0; }}
    li {{ padding: 1rem 0; border-bottom: 1px solid #eee; }}
    h2 {{ font-size: 1.05rem; margin: 0; }}
    .meta, .date, .foot {{ color: #888; font-size: .8rem; }}
    .sample {{ background: #fff3cd; padding: .5rem .75rem; border-radius: 6px; font-size: .85rem; }}
    a {{ font-size: .85rem; }}
  </style>
</head>
<body>
  <h1>이번 주 코스트코 추천 {len(items)}선</h1>
  <p class="date">{date.today().isoformat()} 업데이트</p>
  {banner}
  <ol>
{cards}
  </ol>
  <p class="foot">AI가 웹검색으로 고른 추천이라 가격과 재고는 매장에서 확인해 주세요.</p>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    if args.sample:
        items = json.loads((HERE / "sample_items.json").read_text(encoding="utf-8"))
    else:
        from picker import pick_items

        items = pick_items(market=os.environ.get("COSTCO_MARKET", "한국"))

    (HERE / "index.html").write_text(render(items, args.sample), encoding="utf-8")
    print(f"index.html 생성 ({len(items)}개)")


if __name__ == "__main__":
    main()
