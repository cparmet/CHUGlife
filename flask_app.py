
# A very simple Flask Hello World app for you to get started with...
# https://blog.pythonanywhere.com/121/

from flask import Flask, redirect, render_template, request, url_for
import back_end as be

app = Flask(__name__)
app.config["DEBUG"] = True

comments = []
IG_links = [] # These are the urls to the jpgs
captions = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        global comments
        global IG_links
        global captions


        # To get the html page to iterate through both jpgs and captions, use the zip method.
        # from https://stackoverflow.com/questions/21306134/iterating-over-multiple-lists-in-python-flask-jinja2-templates

        images_and_captions = zip(IG_links, captions)
        comments_to_display=list(comments) # "list" here just means copy to new list, before we reset it.

        comments=[] # Reset for next round
        IG_links=[] # ''
        captions=[] # ''

        return render_template("main_page.html", comments=comments_to_display, images_and_captions=images_and_captions)

    if request.method == 'POST':
        search_term=request.form["search_term"]

        comments, IG_links, captions = be.CHUG_it(search_term,comments)

        # This next block selects the appropriate grammar for the announcement text, depending on the number of posts we found and how to make the search_term plural
        if len(IG_links)==1:
            comments.append("Here's your " + search_term + ".")
        if len(IG_links)>1:
            if (search_term[-1] in 'xz') or (search_term[-2:-1] in 'chsh'): # Does the search_term end in x, z, ch, or sh?
                comments.append("Here are your " + search_term + "es" + ".") # Then the plural form is -es
            elif search_term[-1] == 's':
                comments.append("Here are your " + search_term + ".")  # It already ends in -s. That makes grammatical sense, so keep it as is.
            else:
                comments.append("Here are your " + search_term + "s" + ".")  # Otherwise, add -s to make it plural.

        # This tells browser "Please request this page again, this time using a 'GET' method", so that the user can see the results of their post
        return redirect(url_for('index'))

