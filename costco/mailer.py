"""추천 아이템을 메일(텍스트 + HTML)로 만들어 SMTP로 보낸다."""
import os
import smtplib
from datetime import date
from email.message import EmailMessage
from html import escape


def render_text(items: list[dict]) -> str:
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['name']} ({item['category']})")
        lines.append(f"   {item['why']}")
        lines.append(f"   가격: {item['price_note']}")
        lines.append(f"   {item['source_url']}")
        lines.append("")
    return "\n".join(lines)


def render_html(items: list[dict]) -> str:
    rows = []
    for i, item in enumerate(items, 1):
        rows.append(
            f"""<tr><td style="padding:12px 0;border-bottom:1px solid #eee">
<div style="font-size:16px;font-weight:600">{i}. {escape(item['name'])}</div>
<div style="color:#888;font-size:12px">{escape(item['category'])} · {escape(item['price_note'])}</div>
<div style="margin-top:6px;font-size:14px">{escape(item['why'])}</div>
<div style="margin-top:6px;font-size:12px"><a href="{escape(item['source_url'], quote=True)}">근거 보기</a></div>
</td></tr>"""
        )
    return f"""<!doctype html>
<html lang="ko"><body style="font-family:-apple-system,'Malgun Gothic',sans-serif;max-width:560px;margin:0 auto;padding:16px;color:#222">
<h2 style="margin:0 0 4px">이번 주 코스트코 추천 {len(items)}선</h2>
<div style="color:#888;font-size:12px;margin-bottom:12px">{date.today().isoformat()} 발송</div>
<table style="width:100%;border-collapse:collapse">{''.join(rows)}</table>
<p style="color:#aaa;font-size:11px;margin-top:16px">AI가 웹검색으로 고른 추천이라 가격과 재고는 매장에서 확인해 주세요.</p>
</body></html>"""


def build_message(items: list[dict], sender: str, recipients: list[str]) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"[Costco 위클리] {date.today().isoformat()} 이번 주 추천 {len(items)}선"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(render_text(items))
    msg.add_alternative(render_html(items), subtype="html")
    return msg


def send(msg: EmailMessage) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]

    if port == 465:
        server = smtplib.SMTP_SSL(host, port, timeout=30)
    else:
        server = smtplib.SMTP(host, port, timeout=30)
        server.starttls()
    with server:
        server.login(user, password)
        server.send_message(msg)
