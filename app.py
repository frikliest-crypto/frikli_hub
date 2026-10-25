from datetime import datetime

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>frikli_hub</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 480px; margin: 3rem auto; padding: 0 1rem; text-align: center; }
    button { font-size: 1rem; padding: .6rem 1.2rem; }
  </style>
</head>
<body>
  <h1>안녕하세요 👋</h1>
  <p>frikli_hub 웹앱이 실행 중이에요.</p>
  <p id="time">{{ now }}</p>
  <button onclick="refresh()">시간 새로고침</button>
  <script>
    async function refresh() {
      const res = await fetch('/api/time');
      document.getElementById('time').textContent = (await res.json()).time;
    }
  </script>
</body>
</html>
"""


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def index():
    return render_template_string(PAGE, now=now_str())


@app.route("/api/time")
def api_time():
    return jsonify(time=now_str())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
