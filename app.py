import os
import requests
import random
from flask import Flask, render_template

app = Flask(__name__)
app.config["api_url"] = os.environ.get("API_URL", "http://0.0.0.0:8080")


@app.route("/")
@app.route("/index")
def index():
    # get 3 popular plugins
    try:
        req = requests.get(
            app.config["api_url"] + "/plugins?sort=stars&desc=True", timeout=5
        )
        pop_plugins = req.json()
        pop_plugins = pop_plugins[:3]
    except requests.exceptions.Timeout:
        app.logger.error(
            "Timeout when calling API: %s",
            app.config["api_url"] + "/plugins?sort=stars&desc=True",
        )
        pop_plugins = []

    # get 3 latest plugins
    try:
        req = requests.get(
            app.config["api_url"] + "/plugins?sort=last_updated&desc=True", timeout=5
        )
        latest_plugins = req.json()
        latest_plugins = latest_plugins[:3]
    except requests.exceptions.Timeout:
        app.logger.error(
            "Timeout when calling API: %s",
            app.config["api_url"] + "/plugins?sort=last_updated&desc=True",
        )
        latest_plugins = []

    return render_template(
        "index.html", pop_plugins=pop_plugins, latest_plugins=latest_plugins
    )


@app.route("/popular")
def popular():
    try:
        req = requests.get(
            app.config["api_url"] + "/plugins?sort=stars&desc=True", timeout=5
        )
        plugins = req.json()
    except requests.exceptions.Timeout:
        app.logger.error(
            "Timeout when calling API: %s",
            app.config["api_url"] + "/plugins?sort=stars&desc=True",
        )
        plugins = []

    colors = ["primary", "secondary", "accent", "purple"]
    for p in plugins:
        p["bg_color"] = "bg-" + random.choice(colors) + "-300"

    return render_template("popular.html", plugins=plugins)


if __name__ == "__main__":
    app.run(debug=True)
