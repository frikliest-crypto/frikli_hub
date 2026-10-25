"""Claude + 웹검색으로 이번 주 코스트코 추천 아이템을 고른다."""
import json
from datetime import date

import anthropic

MODEL = "claude-opus-5-5"
MAX_PAUSE_TURNS = 5

ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "category": {"type": "string"},
        "why": {"type": "string"},
        "price_note": {"type": "string"},
        "source_url": {"type": "string"},
    },
    "required": ["name", "category", "why", "price_note", "source_url"],
    "additionalProperties": False,
}

SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": ITEM_SCHEMA}},
    "required": ["items"],
    "additionalProperties": False,
}

PROMPT = """오늘은 {today}입니다. {market} 코스트코에서 이번 주에 구입할 만한 가장 유용하고 인기 있는 아이템 {count}개를 엄선해 주세요.

선정 기준:
- 웹검색으로 최근 후기, 베스트셀러, 커뮤니티 추천, 할인 정보를 확인하고 근거가 있는 상품만 고릅니다.
- 계절과 시기에 맞는 상품, 가성비, 재구매율, 식품·생활용품 등 카테고리 균형을 고려합니다.
- 같은 종류의 상품이 몰리지 않게 합니다.

작성 규칙:
- why: 왜 지금 살 만한지 1~2문장, 한국어로.
- price_note: 검색으로 확인한 가격대만 적고, 확인하지 못했으면 "가격 확인 필요"라고 적습니다. 추측하지 않습니다.
- source_url: 근거로 삼은 페이지 주소.
"""


def pick_items(market: str = "한국", count: int = 10) -> list[dict]:
    client = anthropic.Anthropic()
    messages = [
        {
            "role": "user",
            "content": PROMPT.format(today=date.today().isoformat(), market=market, count=count),
        }
    ]
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}]

    for _ in range(MAX_PAUSE_TURNS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
            tools=tools,
            messages=messages,
        )
        if response.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": response.content})
    else:
        raise RuntimeError("웹검색이 끝나지 않았어요. 다시 시도해 주세요.")

    if response.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError(f"응답을 사용할 수 없어요: stop_reason={response.stop_reason}")

    text = next(b.text for b in reversed(response.content) if b.type == "text")
    items = json.loads(text)["items"]
    if len(items) != count:
        raise RuntimeError(f"{count}개를 요청했는데 {len(items)}개가 왔어요.")
    return items
