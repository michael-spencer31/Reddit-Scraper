import os
import re
import requests
import praw
import configparser
import concurrent.futures
import argparse
import matplotlib.pyplot as plt

class redditCommentScraper:
    def __init__(self, sub, limit):
        config = configparser.ConfigParser()
        config.read('conf.ini')
        self.limit = limit
        self.sub = sub

        # use the praw api and import the users key and secret keys 
        self.reddit = praw.Reddit(client_id=config['REDDIT']['client_id'],
                                  client_secret=config['REDDIT']['client_secret'],
                                  user_agent='Web Scrap')

    def getComments(self):
        subredditname = self.sub 

        subreddit = self.reddit.subreddit(subredditname)
        top_subbreddit = subreddit.top()
        count = 0
        max = 1000
        print('auth success')
        words = []
        wordCount = {}

        # list of common words- we ignore these in our count
        commonWords = {'it','then', 'that','this','and','of','the','for','I','it','has','in',
        'you','to','was','but','have','they','a','is','','be','on','are','an','or',
        'at','as','do','if','your','not','can','my','their','them','they','with',
        'at','about','would','like','there','You','from','get','just','more','so',
        'me','more','out','up','some','will','how','one','what',"don't",'should',
        'could','did','no','know','were','did',"it's",'This','he','The','we',
        'all','when','had','see','his','him','who','by','her','she','our','thing','-',
        'now','what','going','been','we',"I'm",'than','any','because','We','even',
        'said','only','want','other','into','He','what','i','That','thought',
        'think',"that's",'Is','much'}

        for submission in subreddit.top(limit=500):
            submission.comments.replace_more(limit=0)

            for top_level_comment in submission.comments:
                count+= 1

                if(count == max):
                    break
                word = ""
                for letter in top_level_comment.body:
                    if(letter == ' '):
                        if(word and not word[-1].isalnum()):
                            word = word[:-1]
                        if not word in commonWords:
                            words.append(word)
                        word = ""
                    else:
                        word += letter
            if(count == max):
                break

        for word in words:
            if word in wordCount:
                wordCount[word] += 1
            else:
                wordCount[word] = 1

        sortedList = sorted(wordCount, key = wordCount.get, reverse = True)

        keyWords = []
        keyCount = []
        amount = 0 

        for entry in sortedList:
            keyWords.append(entry)
            keyCount.append(wordCount[entry])
            amount += 1

            if(amount == 10):
                break

        labels = keyWords
        sizes = keyCount

        plt.title('Top Comments for: r/' + subredditname)
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        plt.axis('equal')
        plt.show()

class redditImageScraper:
    def __init__(self, sub, limit, order):
        config = configparser.ConfigParser()
        config.read('conf.ini')
        self.sub = sub
        self.limit = limit
        self.order = order
        self.path = f'images/{self.sub}/'

        # use the praw api and import the users key and secret keys 
        self.reddit = praw.Reddit(client_id=config['REDDIT']['client_id'],
                                  client_secret=config['REDDIT']['client_secret'],
                                  user_agent='Web Scrap')

    def download(self, image):
        r = requests.get(image['url'])
        with open(image['fname'], 'wb') as f:
            f.write(r.content)

    def start(self):

        print("Starting to scrap. This make take a few seconds depending on how many images you want.")
        images = []
        try:
            go = 0

            # how will we sort the posts
            if self.order == 'hot':
                submissions = self.reddit.subreddit(self.sub).hot(limit=None)
            elif self.order == 'top':
                submissions = self.reddit.subreddit(self.sub).top(limit=None)
            elif self.order == 'new':
                submissions = self.reddit.subreddit(self.sub).new(limit=None)

            for submission in submissions:
                if not submission.stickied and submission.url.endswith(('jpg', 'jpeg', 'png' , 'gif')) :
                    
                    fname = self.path + re.search('(?s:.*)\w/(.*)', submission.url).group(1)
                    if not os.path.isfile(fname):
                        images.append({'url': submission.url, 'fname': fname})
                        go += 1

                        # once we have collected enough images quit the loop
                        if go >= self.limit:
                            break
            if len(images):

                if not os.path.exists(self.path):
                    # make a new directory to store images in
                    os.makedirs(self.path)
                with concurrent.futures.ThreadPoolExecutor() as ptolemy:
                    ptolemy.map(self.download, images)

            print("Scraping complete!")
        except Exception as e:
            print(e)

def main():

    print("Welcome to my Web Scraper!")
    subreddit = input( "Which subreddit would you like to scrap?")
    images = int(input("How many images would you like to get?"))
    thread = input("Which thread would you like? (new/top/hot)")
    scraper = redditImageScraper(subreddit, images, thread)

    commentscraper = redditCommentScraper(subreddit, images)
    # commentscraper.getComments()
    scraper.start()

if __name__ == '__main__':
    main()
