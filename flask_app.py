
# The Flask app to connect the CHUG Life web page to the Python code that searches Instagram.
# Based on Flask form app: https://blog.pythonanywhere.com/121/

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

        # To get the html page to iterate through both jpgs and captions, I use the zip method.
        # from https://stackoverflow.com/questions/21306134/iterating-over-multiple-lists-in-python-flask-jinja2-templates

        images_and_captions = zip(IG_links, captions)
        comments_to_display=list(comments) # "list" here just means copy to new list, before we reset it.

        comments=[] # Reset for next round
        IG_links=[] # ''
        captions=[] # ''

        return render_template("main_page.html", comments=comments_to_display, images_and_captions=images_and_captions)

    if request.method == 'POST':

        search_term=request.form["search_term"]

        # Gracefully handle blank search.
        if search_term =='':
            comments.append("Here's a photo of a snowy owl covered in snow standing on a glacier. (No search term received.)")
            return redirect(url_for('index'))

        # If the search_term ends in 's' and it's at least 4 letters long,
        # cut off the s. So if you search for 'jays', CHUG will search for 'jay'
        # Added exception for 'Ibis' that Doug found.

        if (search_term[-1] == 's') and (len(search_term)>=4) and search_term.lower()!='ibis':
            search_term = search_term[0:-1]

        # Pull the results
        comments, IG_links, captions = be.CHUG_it(search_term,comments)

        # Announce results!
        # This next block selects the appropriate grammar for the announcement text,
        # depending on the number of posts we found and how to make the search_term plural

        # One result
        if len(IG_links)==1:
            comments.append("Here's your " + search_term + ".")

        # Multiple results
        if len(IG_links)>1:
            if (search_term[-1] in 'xz') or (search_term[-2:] == 'ch') or (search_term[-2:]=='sh'): # Does the search_term end in x, z, ch, or sh?
                comments.append("Here are your " + search_term + "es" + ".") # Then the plural form is -es
            elif search_term[-1] == 's':
                comments.append("Here are your " + search_term + ".")  # It already ends in -s. That makes grammatical sense, so keep it as is.
            elif search_term == 'deer' or search_term == 'fish' or search_term=='sheep' or search_term=='moose':
                comments.append("Here are your " + search_term + ".")  # We shan't pluralize these!
            elif search_term == 'goose':
                comments.append("Here are your geese.")
            else:
                comments.append("Here are your " + search_term + "s" + ".")  # Otherwise, add -s to make it plural.

        # This tells browser "Please request this page again, this time using a 'GET' method", so that the user can see the results of their post
        return redirect(url_for('index'))

