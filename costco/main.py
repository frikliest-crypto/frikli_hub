"""위클리 코스트코 추천 메일.

  python main.py --dry-run   샘플 데이터로 메일을 만들어 preview.html만 저장 (키 불필요)
  python main.py --preview   실제로 아이템을 고르고 preview.html만 저장 (발송 안 함)
  python main.py             아이템을 고르고 메일 발송
"""
import argparse
import json
import os
from pathlib import Path

from mailer import build_message, render_html, send

HERE = Path(__file__).parent


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        items = json.loads((HERE / "sample_items.json").read_text(encoding="utf-8"))
    else:
        from picker import pick_items

        items = pick_items(market=os.environ.get("COSTCO_MARKET", "한국"))

    if args.dry_run or args.preview:
        (HERE / "preview.html").write_text(render_html(items), encoding="utf-8")
        print(f"preview.html 저장 ({len(items)}개)")
        return

    recipients = [a.strip() for a in os.environ["MAIL_TO"].split(",") if a.strip()]
    sender = os.environ.get("MAIL_FROM") or os.environ["SMTP_USER"]
    send(build_message(items, sender, recipients))
    print(f"발송 완료: {', '.join(recipients)}")


if __name__ == "__main__":
    main()
