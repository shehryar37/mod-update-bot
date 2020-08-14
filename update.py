# Python libraries
import os

# Scheduling libraries
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Discord API Libraries
import discord
from discord.ext import commands

# Utilities
import utils

# PostGreSQL
import psycopg2


def main():
    discord_client = commands.Bot(command_prefix='.')

    @discord_client.event
    async def on_ready():

        channels = [discord_client.get_channel(
            channel_id) for channel_id in utils.channel_ids]

        # Creates an asynchronous scheduler
        scheduler = AsyncIOScheduler()
        # [] in the third parameter is used to pass in parameters to the callable function
        scheduler.add_job(check_mod_list, 'interval', [channels], hours=1)
        scheduler.start()

    print("Accessed Discord from update.py")
    discord_client.run(os.environ["CLIENT_TOKEN"])

    discord_client.logout()
    exit(1000)


async def check_mod_list(channels):
    print("MOD UPDATE -- START")
    reddit = utils.reddit_access('update.py')

    # Fetches the mods from the database and converts them into a reddit.Redditor object
    previous_mods = [reddit.redditor(mod) for mod in fetch_mods_db()]

    # Bot accounts that are moderators at r/Animemes
    banned_mods = ['AnimemesBot', 'AnimemesMod', 'SachiMod']
    current_mods = reddit.subreddit('animemes').moderator()
    current_mods = [mod for mod in current_mods if mod.name not in banned_mods]

    added_mods = list(set(current_mods) - set(previous_mods))
    removed_mods = list(set(previous_mods) - set(current_mods))

    # Inserts the moderators into the database
    insert_mods_db(added_mods)
    for mod in added_mods:
        mod_account = reddit.redditor(mod.name)
        mod_account.friend()
        message = '{} has been added as a moderator'.format(mod)
        for channel in channels:
            await channel.send(message)
        print(message)

    # Deletes the moderators from the database
    delete_mods_db(removed_mods)
    for mod in removed_mods:
        mod_account = reddit.redditor(mod)
        mod_account.unfriend()
        message = '{} has been removed as a moderator'.format(mod)
        for channel in channels:
            await channel.send(message)
        print(message)

    print("MOD UPDATE -- END")

    return


def fetch_mods_db():
    try:
        connection = psycopg2.connect(
            os.environ['DATABASE_URL'])

        cursor = connection.cursor()

        query = """SELECT username FROM mod_list"""
        cursor.execute(query)

        return [mod[0] for mod in cursor.fetchall()]

    except (Exception, psycopg2.Error) as error:
        print("Could not fetch the mods from DB: ", error)

    finally:
        if (connection):
            cursor.close()
            connection.close()


def insert_mods_db(added_mods):
    try:
        connection = psycopg2.connect(
            os.environ['DATABASE_URL'])

        cursor = connection.cursor()

        query = """INSERT INTO mod_list VALUES (%s)"""
        mods_insert = cursor.executemany(
            query, [(mod.name, ) for mod in added_mods])
        connection.commit()

        print("{} moderators added to DB".format(cursor.rowcount))

    except (Exception, psycopg2.Error) as error:
        print("Could not insert the mods into DB: ", error)

    finally:
        if (connection):
            cursor.close()
            connection.close()


def delete_mods_db(removed_mods):
    try:
        connection = psycopg2.connect(
            os.environ['DATABASE_URL'])

        cursor = connection.cursor()

        query = """DELETE FROM mod_list WHERE username=%s"""
        mods_delete = cursor.executemany(
            query, [(mod.name, ) for mod in removed_mods])

        connection.commit()

        print("{} moderators removed from DB".format(cursor.rowcount))

    except (Exception, psycopg2.Error) as error:
        print("Could not delete the mods from DB: ", error)

    finally:
        if (connection):
            cursor.close()
            connection.close()


main()
