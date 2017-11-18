
# A very simple Flask Hello World app for you to get started with...
# https://blog.pythonanywhere.com/121/

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DEBUG"] = True

comments = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=comments)

    # Now we're handling POST methods...
    comments.append(request.form["contents"])
    # This tells browser "Please request this page again, this time using a 'GET' method", so that the user can see the results of their post

    return redirect(url_for('index'))
