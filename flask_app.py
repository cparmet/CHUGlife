
# A very simple Flask Hello World app for you to get started with...
# https://blog.pythonanywhere.com/121/

from flask import Flask, render_template

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def index():
    return render_template("main_page.html")

