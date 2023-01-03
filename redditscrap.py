import os
import re
import requests
import praw
import configparser
import concurrent.futures
import argparse
import pandas as pd
import matplotlib.pyplot as plt

class redditCommentScraper:

    def __init__(self, sub):

        config = configparser.ConfigParser()
        config.read('conf.ini')
        self.sub = sub

        # use the praw api and import the users key and secret keys 
        self.reddit = praw.Reddit(client_id=config['REDDIT']['client_id'],
                                  client_secret=config['REDDIT']['client_secret'],
                                  user_agent='Web Scrap')

    def getComments(self):

        # get the name of the subreddit we are going to scrap 
        subredditname = self.sub 

        subreddit = self.reddit.subreddit(subredditname)
        top_subbreddit = subreddit.top()
        count = 0

        # change this value for how many comments you want to scrap
        # note that for any value much > 1000 it will take a while to run
        max = 1000

        print('auth success')
        words = []
        wordCount = {}

        # list of common words- we ignore these in our count
        # add or remove words from here to adjust output
        commonWords = {'Python', 'it', 'It', 'odd', 'then', 'that','this','and','of','the','for','I','it','has','in',
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
                        # check if the word is in our list of common words
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

            # edit this value to change the number of comments in the graph
            if(amount == 10):
                break

        labels = keyWords
        sizes = keyCount

        # create a pie chart using matplot to display comment results 
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

    # this function get information about the posts on a subreddit and loads the data in a pandas dataframe
    def getPosts(self):

        posts = []

        top_posts = self.reddit.subreddit(self.sub).top(limit=self.limit)

        for post in top_posts:
            posts.append([post.title, post.score, post.id, post.subreddit])
        
        posts = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit'])
        print(posts)

    def download(self, image):
        r = requests.get(image['url'])
        with open(image['fname'], 'wb') as f:
            f.write(r.content)

    def start(self):

        print("Starting to scrap. This make take a few seconds depending on how many images you want.")
        images = []

        try:
            go = 0

            # how will we sort the posts (either by hot, top or new posts)
            if self.order == 'hot':
                submissions = self.reddit.subreddit(self.sub).hot(limit=None)
            elif self.order == 'top':
                submissions = self.reddit.subreddit(self.sub).top(limit=None)
            elif self.order == 'new':
                submissions = self.reddit.subreddit(self.sub).new(limit=None)

            for submission in submissions:

                # make sure the submission is a image of some type
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

# main method
def main():

    # print out options menu
    print("Welcome to my Web Scraper!")
    subreddit = input( "Which subreddit would you like to scrap?")
    option = input("What would you like to scrap? (comments/images/posts)")

    if option == 'comments':
        commentscraper = redditCommentScraper(subreddit)
        commentscraper.getComments()
    elif option == 'images':

        images = int(input("How many images would you like to get?"))
        thread = input("Which thread would you like? (new/top/hot)")

        # create the scraper objects to use
        scraper = redditImageScraper(subreddit, images, thread)
        scraper.start()
        # scraper.start()
    elif option == 'posts' or option == 'post':
        postnumber = int(input("How many posts would you like to get?"))
        scraper = redditImageScraper(subreddit, postnumber, 'top')
        scraper.getPosts()
    else:
        print("Invalid option")

if __name__ == '__main__':
    main()
