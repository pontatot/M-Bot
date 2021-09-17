import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=">")

#get a string from the message list
sortname = lambda message, init=1, end=None : " ".join(list(message[init:end]))

#extract id from discord mentions
def getid(message):
    try:
        return int(message.replace("<", "").replace("#", "").replace("@", "").replace("!", "").replace("&", "").replace(">", ""))
    except:
        return None

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    print(message.author.name + "> " + message.content)
    messlist = list(message.content.split(" "))
    if "i'm" in messlist[0].lower() or "im" in messlist[0].lower():
        if "@everyone" not in message.content and "@here" not in message.content and "<@&" not in message.content:
            mention = discord.AllowedMentions(replied_user=False)
            await message.reply(content=f"Hi {sortname(messlist)} I'm M-Bot", allowed_mentions=mention)


    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("pong " + str(round(bot.latency * 1000)) + " ms")

bot.run("TOKEN")
