import os
import requests
import random
import emoji
from datetime import datetime
import time
from flask import Flask, Response, render_template,url_for, request

app = Flask(__name__)
app.config["api_url"] = os.environ.get("API_URL", "http://0.0.0.0:8080")

@app.template_filter('emojify')
def emoji_filter(s):
    return emoji.emojize(s,language="alias")


def humanize_plugin(plugin):
    # find emojis in 

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

def render_languages():
    # get languages (for filtering)
    try:
        languages =  requests.get(
                app.config["api_url"] + "/languages", timeout=5
                        ).json()
    except requests.exceptions.Timeout:
        app.logger.error(
            "Timeout when calling API: %s",
            app.config["api_url"] + "/languages",
        )
        languages = []
    app.logger.info(languages)
    return render_template("filter_languages.html", languages=languages)

@app.route("/filter/languages")
def languages():
    return render_languages()

def render_list_items(sort, order,page, search="") -> str:
    # get plugins from API
    try:
        req = requests.get(
                app.config["api_url"] + f"/plugins?sort={sort}&desc={order}&page={page}{'&search='+search if len(search) else ''}",timeout=5
        )
        plugins = req.json()
    except requests.exceptions.Timeout:
        app.logger.error(
            "Timeout when calling API: %s",
            app.config["api_url"] + f"/plugins?sort={sort}&desc={order}&page={page}",
        )
        plugins = []

    colors = ["primary", "secondary", "accent", "purple"]
    for p in plugins:
        p["bg_color"] = "bg-" + random.choice(colors) + "-300"

    plugins = [humanize_plugin(p) for p in plugins]

    return render_template("list_elements.html", plugins=plugins)


@app.route("/list")
def list_route():
    # read sort and order from query string
    sort = request.args.get("sort", "stars")
    order = request.args.get("desc", "True")
    page = request.args.get("page", "1")
    search = request.args.get("search", "")

    return render_list_items(sort, order,page, search=search)


@app.route("/plugins")
def plugins():
    """
    The general list view for plugins
    """
    sorting_options = ["name","stars","last_updated"]
    sort = request.args.get("sort", "stars")
    if not sort  in sorting_options:
        return Response(f"Bad Request: {sort} is not a valid sorting value. only [{sorting_options}] are valid ☝️.")
    
    order = request.args.get("desc", "True")
    if not order in ["True","False"]:
        return Response(f"Bad Request: {order} is not a valid order value. only [True,False] are valid ☝️.")

    # get and render listview
    list_items = render_list_items(sort,order,1)
    languages = render_languages()

    return render_template("plugins.html", list_items=list_items, languages=languages)

@app.route("/plugin/<author>/<name>")
def plugin(author, name):
    # check if author and name are valid
    if not author or not name:
        return Response(
            "Bad Request: author and name are required parameters", status=400
        )

    # get plugin from API
    try:
        req = requests.get(
            app.config["api_url"] + f"/plugin/{author}/{name}", timeout=5
        )
        
        # check if request was successful
        if req.status_code != 200:
            return Response(
            f"Bad Request: {author}/{name} is not a valid plugin", status=400
            )

        plugin = req.json()
    except requests.exceptions.Timeout:
        app.logger.error(
            "Timeout when calling API: %s",
            app.config["api_url"] + f"/plugin/{author}/{name}",
        )
        plugin = {}
    # humanize the data
    plugin = humanize_plugin(plugin)
    return render_template("plugin_detail.html", plugin=plugin)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/getting-started")
def getting_started():
    return render_template("getting-started.html")

if __name__ == "__main__":

    app.add_url_rule('/favicon.ico',
                 redirect_to=url_for('static', filename='favicon.ico'))
    app.run(debug=True,threaded=True)
