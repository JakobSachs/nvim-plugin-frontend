import os
import requests
import random
from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)
app.config["api_url"] = os.environ.get("API_URL", "http://0.0.0.0:8080")

def humanize_plugin(plugin):
    # humanize stars
    stars = int(plugin["stars"])
    if stars > 1000:
        plugin["stars"] = "{:.1f}k".format(stars / 1000)
    else:
        plugin["stars"] = "{:,}".format(plugin["stars"])

    # humanize last updated by calculating the difference 
    # between last_updated and current date
    last_updated = plugin["last_updated"]["$date"]
    last_updated = last_updated.replace("Z", "+00:00") # add timezone to be UTC
    dt = datetime.fromisoformat(last_updated)
    now = datetime.now(tz=dt.tzinfo)
    diff = now - dt

    # humanize the difference
    if diff.days > 0:
        diff = "{}d".format(diff.days)
    elif diff.seconds > 3600:
        diff = "{}hrs".format(diff.seconds // 3600)
    elif diff.seconds > 60:
        diff = "{}m".format(diff.seconds // 60)
    else:
        diff = "{}s".format(diff.seconds)

    plugin["last_updated"] = "{} ago".format(diff)
    return plugin

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

    # humanize the data
    pop_plugins = [humanize_plugin(p) for p in pop_plugins]
    latest_plugins = [humanize_plugin(p) for p in latest_plugins]

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

    plugins = [humanize_plugin(p) for p in plugins]

    return render_template("popular.html", plugins=plugins)


if __name__ == "__main__":
    app.run(debug=True)
