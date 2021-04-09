import discord
from discord.ext import commands

import datetime
from pyzotero import zotero

import os

LIBRARY_ID = os.environ.get("LIBRARY_ID")
LIBRARY_TYPE = os.environ.get("LIBRARY_TYPE")
ZOTERO_API_KEY = os.environ.get("ZOTERO_API_KEY")
DISCORD_KEY = os.environ.get("DISCORD_KEY")

BASE_URL = "https://www.zotero.org"


zot = zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, ZOTERO_API_KEY)

bot = commands.Bot(command_prefix=commands.when_mentioned_or('^'))

@bot.command()
async def save(context):
    if context.message.reference is None:
        await context.send("Sorry. I don't know what to save")
    else:
        ref = context.message.reference
        server = bot.get_guild(ref.guild_id)
        channel = server.get_channel(ref.channel_id)
        message = await channel.fetch_message(ref.message_id)
        for i in message.embeds:
            template = zot.item_template('webpage')
            template['title'] = i.title
            template['url'] = i.url
            template['creators'][0]['lastName'] = message.author.name
            template['creators'][0]['firstName'] = message.author.discriminator
            template['date'] = str(datetime.datetime.today())
            template['extra'] = i.description
            print(template)
            resp = zot.create_items([template])

            if len(resp['failed']) != 0:
                await context.send("Failed saving embed")
            else:
                await context.send("Saved embed")

@bot.command()
async def url(context):
    await context.send(f"{BASE_URL}/groups/{zot.library_id}")

@bot.command()
async def top5(context):
    items = zot.top(limit=5)
    # we've retrieved the latest five top-level items in our library
    # we can print each item's item type and ID
    for item in items:
        await context.send(f"Item: {item['data']['itemType']} | Url: {item['data']['url']}")

bot.run(DISCORD_KEY)