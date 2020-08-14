import praw
import os

channel_ids = [742799267294609448]
# add 743486931836338267


def reddit_access(file):
    try:
        reddit = praw.Reddit(username=os.environ["USERNAME"],
                             password=os.environ["PASSWORD"],
                             client_id=os.environ["CLIENT_ID"],
                             client_secret=os.environ["CLIENT_SECRET"],
                             user_agent=os.environ["USER_AGENT"]
                             )

        print("Accessed Reddit from {}".format(file))

        return reddit

    except Exception as e:
        print(e)
        exit(1)
