from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)
VERSION = "v1"

# Our grocery list (kept in memory for now)
groceries = [
    {"name": "Milk", "qty": 1},
    {"name": "Eggs", "qty": 12},
]

PAGE = """
<!doctype html>
<html>
<head>
  <title>Grocery App</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 500px; margin: 40px auto; padding: 0 16px; }
    h1 { color: #2e7d32; }
    li { margin: 8px 0; }
    form.inline { display: inline; }
    .version { color: gray; font-size: 12px; }
  </style>
</head>
<body>
  <h1>🛒 My Grocery List</h1>
  <ul>
    {% for item in items %}
      <li>{{ item.name }} x {{ item.qty }}
        <form class="inline" method="post" action="/delete/{{ loop.index0 }}">
          <button>Bought ✔</button>
        </form>
      </li>
    {% else %}
      <li>Nothing to buy! 🎉</li>
    {% endfor %}
  </ul>
  <form method="post" action="/add">
    <input name="name" placeholder="Item (e.g. Bread)" required>
    <input name="qty" type="number" value="1" min="1" style="width:60px">
    <button>Add</button>
  </form>
  <p class="version">Version: {{ version }}</p>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE, items=groceries, version=VERSION)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    qty = request.form.get("qty", "1")
    if name:
        groceries.append({"name": name, "qty": int(qty) if qty.isdigit() else 1})
    return redirect("/")

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    if 0 <= index < len(groceries):
        groceries.pop(index)
    return redirect("/")

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
