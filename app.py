from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from collections import Counter
import random
import math

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# 抓200期
# =========================
def fetch_history(limit=200):
    url = "https://nx4.988cp.net/history?g=BingoBingo"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        draws = []
        for row in soup.select("div, tr"):
            nums = [int(x) for x in row.get_text().split() if x.isdigit()]
            if len(nums) == 20:
                draws.append(nums)
            if len(draws) >= limit:
                return draws[:limit]
    except:
        pass

    return [[i for i in range(1, 21)]] * limit


# =========================
# 建權重
# =========================
def build_weights(draws):
    c = Counter()
    for d in draws:
        c.update(d)
    return {i: c[i] + 1 for i in range(1, 81)}


# =========================
# 選號策略
# =========================
def pick_numbers(weights, count):
    nums = list(weights.keys())
    w = list(weights.values())

    result = set()
    while len(result) < count:
        result.add(random.choices(nums, weights=w, k=1)[0])

    return list(result)


# =========================
# 🎯 1000次回測（核心）
# =========================
def backtest(strategy_nums, history):
    wins = 0
    trials = 1000

    for _ in range(trials):
        draw = random.choice(history)  # 模擬一期

        hit = len(set(strategy_nums) & set(draw))

        # 命中>=3算成功（可調）
        if hit >= 3:
            wins += 1

    return round(wins / trials * 100, 2)


# =========================
# API：選號 + 回測
# =========================
@app.route("/simulate", methods=["POST"])
def simulate():

    count = int(request.json["count"])

    history = fetch_history(200)
    weights = build_weights(history)

    nums = pick_numbers(weights, count)

    win_rate = backtest(nums, history)

    return jsonify({
        "numbers": nums,
        "win_rate": win_rate
    })


# =========================
# 前20期偏移（簡化）
# =========================
@app.route("/drift")
def drift():

    data = fetch_history(20)

    c = Counter()
    for d in data:
        c.update(d)

    exp = (20 * 20) / 80

    result = {}

    for i in range(1, 81):
        obs = c[i]
        z = (obs - exp) / (math.sqrt(exp) + 1e-6)

        result[i] = z

    return jsonify(result)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)