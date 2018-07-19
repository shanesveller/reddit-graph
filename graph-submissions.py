import argparse
import pprint
import praw

from neo4j.v1 import GraphDatabase

parser = argparse.ArgumentParser(description='List titles for a given Subreddit.')

parser.add_argument('subreddit', metavar='subreddit', type=str, help='name of Subreddit')

parser.add_argument('-l', '--limit', metavar='limit', type=int, help='number of titles to fetch', default=10)

parser.add_argument('-u', '--username', metavar='username', type=str, help='Neo4j Username', default='neo4j')

parser.add_argument('-p', '--password', metavar='password', type=str, help='Neo4j Password', default='neo4j')

parser.add_argument('--uri', metavar='uri', type=str, help='Neo4j URI', default='bolt://localhost')

args = parser.parse_args()

driver = GraphDatabase.driver(args.uri, auth=(args.username, args.password))

reddit = praw.Reddit()

subreddit = reddit.subreddit(args.subreddit)

submissions = subreddit.hot(limit=args.limit)

# CREATE CONSTRAINT ON (subr:Subreddit) ASSERT subr.name IS UNIQUE
# CREATE CONSTRAINT ON (user:User) ASSERT user.name IS UNIQUE

def insert_redditor(tx, user):
    author_insert = f'MERGE (user:User {{name:"{user.name}"}}) RETURN user'
    print(author_insert)

    for record in tx.run(author_insert):
        pprint.pprint(record)

def insert_subreddit(tx, subreddit):
    q = f'MERGE (subr:Subreddit {{name:"{subreddit.display_name}"}})'
    print(q)

    for record in tx.run(q):
        pprint.pprint(record)

def user_commented_on(tx, user, subreddit):
    q = f'MERGE (subr:Subreddit {{name:"{subreddit.display_name}"}})'
    print(q)

    q2 = f"""
    MATCH (user:User {{ name: "{user.name}" }}),(subr:Subreddit {{ name: "{subreddit.display_name}" }})
    MERGE (user)-[r:SUBMITTED_TO]->(subr)
    RETURN user.name, type(r), subr.name
    """
    print(q2)

    for record in tx.run(q2):
        pprint.pprint(record)


for submission in submissions:
    # pprint.pprint(vars(submission))

    created_utc = submission.created_utc
    domain = submission.domain
    downvotes = submission.downs
    name = submission.name
    sub_id = submission.id
    over_18 = submission.over_18
    reddit_url = submission.url
    selftext = submission.selftext
    title = submission.title
    upvotes = submission.ups

    # pprint.pprint(vars(author))

    with driver.session() as session:
        inserted_subr = session.write_transaction(insert_subreddit, submission.subreddit)
        inserted_user = session.write_transaction(insert_redditor, submission.author)
        user_commented = session.write_transaction(user_commented_on, submission.author, submission.subreddit)
