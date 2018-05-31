# Download the IG posts
# Clean the data, patching anomalies

import pandas as pd
# import numpy as np
# import regex

def download_all_photochug_posts():
    data, cursor = ie.user('photochug')
    downloaded_posts_df = pd.DataFrame(data['media']['nodes'])

    for i in range(10):  # 10 runs to grab up to 12 posts each, N=120 max
        posts_more, cursor = ie.user('photochug', cursor)
        posts_more_df = pd.DataFrame(posts_more['media']['nodes'])
        downloaded_posts_df = pd.concat([downloaded_posts_df, posts_more_df], ignore_index=True)
        #     time.sleep(0.1)
    return downloaded_posts_df

def patch_captions_that_are_NAN_or_anomaly(data_df_unpatched,comments):
    '''
    This function fixes captions that are entered differently on Instagram.
    It uploads patches from an XLS file (CSV was finnicky) and applies them.
    '''

    data_df_patched = data_df_unpatched.copy()

    # Import my patches
    Anomaly_fix = pd.read_excel('/home/cparmet/chuglife/patches.xls', header=0)

    # Force column names to import exactly as I want to refer to them. May no longer be a problem, but was an issue with CSVs.
    Anomaly_fix.columns = ['display_src', 'caption']
    Anomaly_fix.set_index('display_src', inplace=True)

    # Iterate through rows in the patch table (CSV)
    # Remember, about these indices:
    # - In patch table, display_src is only the jpg name, to fix an issue with IG servers changing.
    # - In IG_download, indices are sequential integers that will change as we post more photos.

    for i in Anomaly_fix.index:

        # Find the indices in downloaded IG data that match the rows I have in Anomaly_fix csvIG_match_for_this_patch_row = data_df_patched.loc[data_df_patched['display_src'] == i]

        # IG_match_for_this_patch_row = data_df_patched.loc[data_df_patched['display_src'] == i]

        matches=0
        for j in data_df_patched.index:
            if i in data_df_patched.ix[j, 'display_src']:
                index_of_IG_data_to_patch = j
                matches+=1 # If there's more than 1 match, this 'for' loop will only save the last match. But this counter will be >1.

        ########
        # Soft QC. Use this opportunity for extra QC of the downloaded IG data.
        # All display_srcs from the Anomaly_fix CSV should be in downloaded IG data
        if matches == 0:
            comments.append('Warning: A post in patch CSV was not downloaded from IG.')
            continue

        if matches > 1:  # Each display_src should only occur once
            comments.append("Error: I have duplicate posts in downloads. Should've been de-duped by now.")
            # comments.append(IG_match_for_this_patch_row)
            # Just keep the first one. Cuz really, all that matters in this kind of a database is that it's there once.
            # IG_match_for_this_patch_row = IG_match_for_this_patch_row.head(1)

            # At this point, we've ensured IG_match_for_this_patch_row is only 1 match.
        ########

        data_df_patched.ix[index_of_IG_data_to_patch, 'caption'] = Anomaly_fix.ix[i, 'caption']

    return data_df_patched, comments


def check_for_null_captions(posts_df,comments):
    ''' QC: any null captions remain? Then give a soft warning'''

    null_captions_df = posts_df.ix[posts_df.caption.isnull(), 'display_src']

    if len(null_captions_df) != 0:
        comments.append('Warning: Null captions:')
        comments.append(list(null_captions_df))

    return comments



def CHUG_it(search_term,comments):
    IG_links=[]
    captions=[]

    posts_df = download_all_photochug_posts()
    posts_df.drop_duplicates(subset=['display_src'], inplace=True)

    # QC:
    comments.append('Reviewed '+ str(len(posts_df)) + ' photos.')

    posts_df,comments = patch_captions_that_are_NAN_or_anomaly(posts_df,comments)

    # QC: Check if there are any more NAN captions I didn't patch. If so, soft warning
    comments=check_for_null_captions(posts_df,comments)

    search_term=str(search_term).lower()
    j = 0

    for i in posts_df.index:
        this_post_caption=posts_df.ix[i, 'caption']

        if search_term in str(this_post_caption).lower(): # Make them both lowercase for the match, so it's case-insensitive
            IG_links.append(posts_df.ix[i, 'display_src'])
            captions.append(this_post_caption)
            j += 1
            continue

        # If we didn't find a match with the whole word, maybe we will if we strip out the blank spaces?
        # So, search for "blue jay" also as "bluejay" Like a hashtag
        if ' ' in search_term and search_term.replace(' ', '') in str(this_post_caption).lower():
            IG_links.append(posts_df.ix[i, 'display_src'])
            captions.append(this_post_caption)
            j += 1


    if j == 0:
        comments.append('No matches, CHUG.')

    return comments,IG_links,captions
