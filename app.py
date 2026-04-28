from flask import Flask, render_template, request, jsonify
import random
import datetime
from collections import Counter

app = Flask(__name__)

# =========================
# 模擬抓2000筆資料
# =========================
def get_data():
    data = []
    for _ in range(2000):
        data.append(random.sample(range(1, 81), 20))
    return data

# =========================
# 星期過濾
# =========================
def filter_weekday(data):
    weekday = datetime.datetime.now().weekday()
    return [d for i, d in enumerate(data) if i % 7 == weekday]

# =========================
# 統計權重
# =========================
def build_weights(data):
    c = Counter()
    for d in data:
        c.update(d)
    return {i: c[i] + 1 for i in range(1, 81)}

# =========================
# 選號
# =========================
def pick_numbers(weights, count):
    nums = list(weights.keys())
    w = list(weights.values())
    result = set()

    while len(result) < count:
        result.add(random.choices(nums, weights=w, k=1)[0])

    return sorted(result)

# =========================
# API
# =========================
@app.route("/pick", methods=["POST"])
def pick():
    count = int(request.json["count"])

    data = get_data()
    data = filter_weekday(data)
    weights = build_weights(data)

    result = pick_numbers(weights, count)

    return jsonify({
        "numbers": result,
        "weekday": datetime.datetime.now().strftime("%A")
    })

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)