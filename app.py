from flask import Flask, request, redirect, session, render_template_string

app = Flask(__name__)
app.secret_key = "mock_secret_key_12345"

SECRET_TOKEN = "superSecretToken"
LOGIN = "aa"
PASSWORD = "aabb"

SIGNIN_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Sign In</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }
        .login-box { background: white; padding: 32px 40px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); min-width: 300px; }
        h2 { margin: 0 0 24px; color: #333; }
        label { display: block; margin-bottom: 4px; color: #555; font-size: 14px; }
        input[type=text], input[type=password] { width: 100%; padding: 8px 10px; margin-bottom: 16px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
        button { width: 100%; padding: 10px; background: #337ab7; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 15px; }
        button:hover { background: #286090; }
        {% if error %}.error { color: #a94442; font-size: 13px; margin-bottom: 12px; }{% endif %}
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Login</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST" action="/signin" enctype="application/x-www-form-urlencoded">
            <input type="hidden" name="__secretToken" value="{{ token }}">
            <label>Login</label>
            <input type="text" name="login" autocomplete="off">
            <label>Password</label>
            <input type="password" name="password">
            <button type="submit">Sign In</button>
        </form>
    </div>
</body>
</html>"""

BASE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; display: flex; flex-direction: column; min-height: 100vh; }
        .navbar { background: #333; color: white; padding: 12px 24px; display: flex; gap: 20px; }
        .navbar a { color: #ccc; text-decoration: none; font-size: 14px; }
        .navbar a:hover { color: white; }
        .container { flex: 1; max-width: 900px; margin: 30px auto; width: 100%; padding: 0 20px; box-sizing: border-box; }
        h3 { color: #444; margin-bottom: 16px; }
        #mainPanel { display: flex; flex-direction: column; gap: 10px; }
        .exception-panel { }
        .alert { padding: 12px 18px; border-radius: 4px; font-size: 14px; border: 1px solid transparent; }
        .alert-success { background-color: #dff0d8; color: #3c763d; border-color: #d6e9c6; }
        .alert-warning { background-color: #fcf8e3; color: #8a6d3b; border-color: #faebcc; }
        .alert-danger  { background-color: #f2dede; color: #a94442; border-color: #ebccd1; }
        #footer { background: #eee; border-top: 1px solid #ddd; padding: 10px 24px; text-align: center; font-size: 13px; color: #666; }
        #footer a { color: #337ab7; text-decoration: none; }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/index">Index</a>
        <a href="/version">Version</a>
        <a href="/signin">Logout</a>
    </div>
    <div class="container">
        <h3>{{ title }}</h3>
        <div id="mainPanel">
            {{ content }}
        </div>
    </div>
    <div id="footer">
        <a href="/api/version" title="15.04.2026 14:01:00">1.2.0.3456</a>
        Server1
    </div>
</body>
</html>"""

# ---------- Hardcoded data ----------

INDEX_ITEMS = [
    ("ServiceManagement", "success"),
    ("ServiceSales",      "success"),
    ("ServiceBilling",    "danger"),
    ("ServiceReports",    "warning"),
    ("ServiceNotify",     "success"),
    ("ServiceAuth",       "danger"),
    ("ServiceExport",     "warning"),
]

VERSION_ITEMS = [
    ("ServiceManagement", "1.2.0.3456", "Server1", "15.04.2026 14:06:47", "success"),
    ("ServiceSales",      "1.2.0.3456", "Server1", "15.04.2026 14:04:04", "success"),
    ("ServiceBilling",    "1.2.0.3455", "Server2", "14.04.2026 09:11:02", "warning"),  # older version
    ("ServiceReports",    "1.2.0.3456", "Server1", "15.04.2026 14:05:30", "success"),
    ("ServiceNotify",     "1.1.0.3100", "Server2", "01.03.2026 08:00:00", "danger"),   # very old
    ("ServiceAuth",       "1.2.0.3456", "Server1", "15.04.2026 14:03:21", "success"),
    ("ServiceExport",     "1.2.0.3455", "Server1", "14.04.2026 22:47:10", "warning"),
]

# ------------------------------------

def render_index_content():
    rows = []
    for name, cls in INDEX_ITEMS:
        rows.append(
            f'<div class="exception-panel">'
            f'<div class="alert alert-{cls}">'
            f'<strong>{name}</strong> - Diagnostic'
            f'</div></div>'
        )
    return "\n".join(rows)

def render_version_content():
    rows = []
    for name, ver, srv, ts, cls in VERSION_ITEMS:
        rows.append(
            f'<div class="exception-panel">'
            f'<div class="alert alert-{cls}">'
            f'<strong>{name}</strong>'
            f' - {ver} ({srv}) ({ts})'
            f'</div></div>'
        )
    return "\n".join(rows)


@app.route("/signin", methods=["GET"])
def signin_get():
    return render_template_string(SIGNIN_TEMPLATE, token=SECRET_TOKEN, error=None)


@app.route("/signin", methods=["POST"])
def signin_post():
    token = request.form.get("__secretToken", "")
    login = request.form.get("login", "")
    password = request.form.get("password", "")

    if token == SECRET_TOKEN and login == LOGIN and password == PASSWORD:
        session["auth"] = True
        return redirect("/index")

    return render_template_string(SIGNIN_TEMPLATE, token=SECRET_TOKEN, error="Invalid credentials"), 401


@app.route("/index")
def index():
    content = render_index_content()
    return render_template_string(BASE_TEMPLATE, title="Index – Diagnostic", content=content)


@app.route("/version")
def version():
    content = render_version_content()
    return render_template_string(BASE_TEMPLATE, title="Version", content=content)


@app.route("/api/version")
def api_version():
    return "1.2.0.3456", 200, {"Content-Type": "text/plain"}


@app.route("/")
def root():
    return redirect("/signin")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
