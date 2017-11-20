
# A very simple Flask Hello World app for you to get started with...
# https://blog.pythonanywhere.com/121/

from flask import Flask, redirect, render_template, request, url_for
import back_end as be
import pandas as pd

app = Flask(__name__)
app.config["DEBUG"] = True

comments = []
IG_links = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        global comments
        global IG_links
        comments_to_display=list(comments) # Copy to new list
        IG_links_to_display=list(IG_links) # Copy to new list
        comments=[] # Reset for next round
        IG_links=[] # Reset for next round
        return render_template("main_page.html", comments=comments_to_display, IG_links=IG_links_to_display)

    if request.method == 'POST':
        search_term=request.form["search_term"]

        comments,IG_links=be.CHUG_it(search_term,comments,IG_links)

        comments.append('Results for '+search_term + '...')
        IG_links.append(IG_links)

        # This tells browser "Please request this page again, this time using a 'GET' method", so that the user can see the results of their post
        return redirect(url_for('index'))

