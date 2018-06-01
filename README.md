# CHUGlife

This web app searches one Instagram (IG) account for specific captions. It displays matching images and captions.

See it in action: [chuglife.chadparmet.com](http://chuglife.chadparmet.com).

## Why create it?
A pair of nature photographers posting at [@PhotoCHUG](https://www.instagram.com/photochug) wanted to use our IG account as a shared database. We wanted to quickly query to see which animal species we've photographed, while in the field or at home reviewing shots.

But instagram doesn't allow users to search for hashtags/captions filtered to only search within the posts of one single account. CHUGLife is a web app to exceute that one type of query.

## Built with
Back end: Beautiful Soup, Pandas, Regex

Front end: Flask, Bootstrap CSS, a little JQuery

The app was modified in Spring 2018 to be more resilient to website changes made on instagram.com. Such changes broke the IG-scraping package I used originally, [Instagram Explore](https://github.com/midnightSuyama/instagram-explore).

Separate from the web app, a Python script runs daily to update a file on AWS S3 that caches the database. The cache was initially loaded with [Instagram Scraper](https://github.com/rarcega/instagram-scraper).

The animated owl on the web page is by the super-talented [Irina Mir](https://dribbble.com/shots/3053961-Owl-head-spin), used with kind permission.