import argparse
import praw

parser = argparse.ArgumentParser(description='List titles for a given Subreddit.')

parser.add_argument('subreddit', metavar='subreddit', type=str, help='name of Subreddit')

parser.add_argument('-l', '--limit', metavar='limit', type=int, help='number of titles to fetch', default=10)

args = parser.parse_args()

reddit = praw.Reddit()

subreddit = reddit.subreddit(args.subreddit)

submissions = subreddit.hot(limit=args.limit)

for submission in submissions:
    print(submission.title)
