# Download the IG posts
# Clean the data

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# import numpy as np
# import regex

def download_cache_of_posts():
    cache_url = 'https://s3.amazonaws.com/chuglife/chugs_cache.xlsx'
    downloaded_posts_df = pd.read_excel(cache_url)
    return downloaded_posts_df

## Functions to scrape Instagram for current posts
def extract_comment(post):
    ''' Extract comment from on-screen post metadata'''
    result = re.search('.+?"}', post)
    comment = result.group(0)[1:-2] # The 1 and -2 are to strip unnecessary characters.
    comment = comment.replace('\\n',' ') # Line breaks. Note here it's two backslashes.
    return comment

def extract_url(post):
    ''' Extract URL from the on-screen posts metadata'''
    # https://stackoverflow.com/questions/6109882/regex-match-all-characters-between-two-strings
    result = re.search('(?<=display_url":")(.*)(?=edge_liked_by)', post)
    return result.group(0)[0:-3]

def merge_cache_with_onscreen(cache_df, on_screen_df):
    ''' Combine the two dataframes'''
    f = lambda path: path.split('/')[-1]
    cache_df['img_name'] = cache_df['display_url'].apply(f)
    on_screen_df['img_name'] = on_screen_df['display_url'].apply(f)

    merged = cache_df.merge(on_screen_df, how='outer', on='img_name')
    merged = merged.fillna('')

    col_rename = {"comment_x": "comment_from_json", "comment_y": "comment_on_screen"}
    merged = merged.rename(index=str, columns=col_rename)

    return merged

def harmonize_comments(merged):
    merged['comment'] = ''

    for i, post in merged.iterrows():
        comment_json = post['comment_from_json']
        comment_screen = post['comment_on_screen']
        comment = ''
        if len(comment_json) <= 1:
            if len(comment_screen) <= 1:
                comment = ''  # Both comments are blank or only 1 character long. No comment.
            else:
                comment = comment_screen  # JSON comment is <=1c long, but on-screen comment isn't. Use latter.
        else:
            if len(comment_screen) <= 1:
                comment = comment_json  # On-screen comment is <=1c long, but JSON isn't. Use latter.
            else:  # Both comments have substance.
                if comment_json == comment_screen:
                    comment = comment_json  # Both comments are the same. Use json
                else:
                    raise ValueError('Error while updating cache of posts with on-screen scrape. Conflict with comments at post: ' + str(post['display_url']))

        merged.ix[i, 'comment'] = comment

    merged = merged.drop(['comment_from_json', 'comment_on_screen'], axis=1)

    return merged


def harmonize_display_url(merged):
    ''' Harmonize display_url from JSON cached posts with that from on-screen scrape.'''
    merged['display_url'] = ''

    for i, post in merged.iterrows():
        url = ''
        url_json = post['display_url_x']
        url_screen = post['display_url_y']

        # Reminder, we've already merged JSON and On-screen DFs using img_name as the key
        # Urls may differ between JSON and On_screen. That's normal.
        # But shouldn't have any duplicate img_names, after the merge.

        if len(url_json) <= 1:
            if len(url_screen) <= 1:
                # Both urls are missing
                raise ValueError(
                    'Error while updating cache of posts with on-screen scrape. Display_url missing at post: ' + str(
                        post))
            else:
                url = url_screen  # JSON has no url, but on-screen scrape did. Use latter.
        else:
            url = url_json  # JSON has a url, but on-screen doesn't. Use that.

        merged.ix[i, 'display_url'] = url

    merged = merged.drop(['display_url_x', 'display_url_y'], axis=1)

    return merged


def update_cache_with_current_posts(cache_df):
    '''Scrape Instagram for the latest posts'''

    user_name = 'photochug'
    url = "https://www.instagram.com/%s/" % user_name
    res = requests.get(url)
    html = BeautifulSoup(res.content, 'html.parser')
    data = res.text.split('"node":{"text":')[1:]

    cols = ['display_url', 'comment']
    on_screen_df = pd.DataFrame(columns=cols)

    # Make a dataframe out of everything on screen
    for i, post in enumerate(data):
        on_screen_df.loc[i, 'display_url'] = extract_url(post)
        on_screen_df.loc[i, 'comment'] = extract_comment(post)

    merged = merge_cache_with_onscreen(cache_df, on_screen_df)
    merged = harmonize_comments(merged)
    merged = harmonize_display_url(merged)

    return merged

# def patch_captions_that_are_NAN_or_anomaly(data_df_unpatched,comments):
#     '''
#     This function fixes captions that are entered differently on Instagram.
#     It uploads patches from an XLS file (CSV was finnicky) and applies them.
#     '''
#
#     data_df_patched = data_df_unpatched.copy()
#
#     # Import my patches
#     Anomaly_fix = pd.read_excel('/home/cparmet/chuglife/patches.xls', header=0)
#
#     # Force column names to import exactly as I want to refer to them. May no longer be a problem, but was an issue with CSVs.
#     Anomaly_fix.columns = ['img_name', 'comment']
#     Anomaly_fix.set_index('img_name', inplace=True)
#
#     # Iterate through rows in the patch table (CSV)
#     # Remember, about these indices:
#     # - In patch table, img_name is only the jpg name, to fix an issue with IG servers changing.
#     # - In IG_download, indices are sequential integers that will change as we post more photos.
#
#     for i in Anomaly_fix.index:
#
#         # Find the indices in downloaded IG data that match the rows I have in Anomaly_fix csvIG_match_for_this_patch_row = data_df_patched.loc[data_df_patched['img_name'] == i]
#
#         # IG_match_for_this_patch_row = data_df_patched.loc[data_df_patched['img_name'] == i]
#
#         matches=0
#         for j in data_df_patched.index:
#             if i in data_df_patched.ix[j, 'img_name']:
#                 index_of_IG_data_to_patch = j
#                 matches+=1 # If there's more than 1 match, this 'for' loop will only save the last match. But this counter will be >1.
#
#         ########
#         # Soft QC. Use this opportunity for extra QC of the downloaded IG data.
#         # All img_name from the Anomaly_fix CSV should be in downloaded IG data
#         if matches == 0:
#             comments.append('Warning: A post in patch CSV was not downloaded from IG.')
#             continue
#
#         if matches > 1:  # Each img_name should only occur once
#             comments.append("Error: I have duplicate posts in downloads. Should've been de-duped by now.")
#             # comments.append(IG_match_for_this_patch_row)
#             # Just keep the first one. Cuz really, all that matters in this kind of a database is that it's there once.
#             # IG_match_for_this_patch_row = IG_match_for_this_patch_row.head(1)
#
#             # At this point, we've ensured IG_match_for_this_patch_row is only 1 match.
#         ########
#
#         data_df_patched.ix[index_of_IG_data_to_patch, 'comment'] = Anomaly_fix.ix[i, 'comment']
#
#     return data_df_patched, comments


def check_for_null_captions(posts_df,comments):
    ''' QC: any null captions remain? Then give a soft warning'''

    null_captions_df = posts_df.ix[posts_df.comment.isnull(), 'img_name']

    if len(null_captions_df) != 0:
        comments.append('Warning, tell Chaddy: Null captions...')
        comments.append(list(null_captions_df))

    return comments


def CHUG_it(search_term,comments):
    IG_links=[]
    captions=[]

    cache_df = download_cache_of_posts()
    posts_df = update_cache_with_current_posts(cache_df)
    posts_df.drop_duplicates(subset=['img_name'], inplace=True)

    # QC:
    comments.append('Reviewed '+ str(len(posts_df)) + ' photos.')

    posts_df,comments = patch_captions_that_are_NAN_or_anomaly(posts_df,comments)

    # QC: Check if there are any more NAN captions I didn't patch. If so, soft warning
    comments=check_for_null_captions(posts_df,comments)

    search_term=str(search_term).lower()
    j = 0

    for i in posts_df.index:
        this_post_caption=posts_df.ix[i, 'comment']

        if search_term in str(this_post_caption).lower(): # Make them both lowercase for the match, so it's case-insensitive
            IG_links.append(posts_df.ix[i, 'display_url'])
            captions.append(this_post_caption)
            j += 1
            continue

        # If we didn't find a match with the whole word, maybe we will if we strip out the blank spaces?
        # So, search for "blue jay" also as "bluejay" Like a hashtag
        if ' ' in search_term and search_term.replace(' ', '') in str(this_post_caption).lower():
            IG_links.append(posts_df.ix[i, 'display_url'])
            captions.append(this_post_caption)
            j += 1


    if j == 0:
        comments.append('No matches, CHUG.')

    return comments,IG_links,captions
