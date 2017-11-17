
# A very simple Flask Hello World app for you to get started with...
# https://blog.pythonanywhere.com/121/

from flask import Flask, redirect, render_template, request, url_for
import back_end as be
import pandas as pd

app = Flask(__name__)
app.config["DEBUG"] = True

comments=[]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        comments_to_display=comments.copy()
        comments=[]
        return render_template("main_page.html", comments=comments_to_display)

    # Now we're handling POST methods...
    search_term=request.form["contents"]
    image_find(search_term)

    return redirect(url_for('index'))


def image_find(search_term):
    posts_df = be.download_all_photochug_posts()
    posts_df.drop_duplicates(subset=['display_src'], inplace=True)

    # QC:
    comments.append('Reviewed '+ str(len(posts_df)) + 'lovely birds.')

    posts_df = be.patch_captions_that_are_NAN_or_anomaly(posts_df)

    # QC: Check if there are any more NAN captions I didn't patch. If so, soft warning
    comments=be.check_for_null_captions(posts_df,comments)

    be.show_search_results(posts_df, search_term)
    return


def show_search_results(posts_df,search_term='heron'):

    print('Results for '+search_term + '...')
    print('-----------------------------')

    j = 0
    for i in posts_df.index:
        if search_term in posts_df.ix[i, 'caption']:
            print(posts_df.ix[i, 'display_src'])
            print(posts_df.ix[i, 'caption'])
            j += 1
            # post_image = posts_df.ix[i, 'display_src']
            # img_code = '<img src=' + post_image + ' height="300" width="300"></img>'

    if j == 0:
        print('No matches, CHUG.')

    print('-----------------------------')

    return