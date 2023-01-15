# Reddit Scraper

Uses the Reddit praw API to scrap Reddit.com. Allows users to download pictures from a subreddit of their choice. Can also find the 10 most commmon words in comments on a subreddit. 

# Output

This is a graph of the 10 most used words in comments on the r/python subreddit.

![Alt text](/RedditScrap.png?raw=true "")

# Usage

You will need to get a client ID and secret from Reddit. Replace XXXXX in conf.ini with your codes and run

```
python3 scraper.py
```
Then, simply follow the instructions the command prompt will give you. If you download pictures, they will be found in a folder with the same name as the subreddit you selected. 
