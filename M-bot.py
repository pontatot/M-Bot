import os
import discord
from discord.ext import commands
import youtube_dl
import random
import json
from keep_alive import keep_alive

bot = commands.Bot(command_prefix=">")

with open("help.json", "r") as help_file:
    helpPage = json.load(help_file)

#get a string from the message list
sortname = lambda message, init=1, end=None : " ".join(list(message[init:end]))

#extract id from discord mentions
def getid(message):
    try:
        return int(message.replace("<", "").replace("#", "").replace("@", "").replace("!", "").replace("&", "").replace(">", ""))
    except:
        return None

def findSong(arg):
    found = []
    for file in os.listdir("./music/"):
        if arg.lower() in file.lower():
            found.append(file)
    return found

def listToString(files):
    result = ""
    for i in range(len(files)):
        result += str(i+1) + ") " + files[i] + "\n"
    return result

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    print(message.author.name + "> " + message.content)
    messlist = list(message.content.split(" "))
    








    await bot.process_commands(message)





@bot.command()
async def ping(ctx):
    embed = discord.Embed(title="Pong", description=f"{round(bot.latency * 1000)} ms", colour=0x79A4F9)
    mention = discord.AllowedMentions(replied_user=False)
    await ctx.reply(content=None, embed=embed, allowed_mentions=mention)


@bot.command()
async def join(ctx, id: int = 0):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if id != 0:
        channel = bot.get_channel(id)
        await channel.connect()
        embed = discord.Embed(title="Joined voice channel", description=channel.mention, colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)
    elif ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        embed = discord.Embed(title="Joined voice channel", description=channel.mention, colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)
    else:
        embed = discord.Embed(title="Could not join voice channel", description="Make sure you are connected to a voice channel", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)


@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if ctx.guild.voice_client:
        channel = ctx.guild.voice_client
        await channel.disconnect()
        embed = discord.Embed(title="Left voice channel", description=channel.channel.mention, colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)
    else:
        embed = discord.Embed(title="Currently not in a voice channel", description="", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        if voice.is_playing():
            voice.pause()
            embed = discord.Embed(title="Paused", description="", colour=0x79A4F9)
            await ctx.channel.send(content=None, embed=embed)
        elif voice.is_paused():
            voice.resume()
            embed = discord.Embed(title="Resumed", description="", colour=0x79A4F9)
            await ctx.channel.send(content=None, embed=embed)
        else:
            embed = discord.Embed(title="Not playing audio", description="", colour=0x79A4F9)
            await ctx.channel.send(content=None, embed=embed)
    else:
        embed = discord.Embed(title="Currently not in a voice channel", description="", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        voice.stop()
        embed = discord.Embed(title="Stopped", description="", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)
    else:
        embed = discord.Embed(title="Currently not in a voice channel", description="", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)


@bot.command()
async def download(ctx, link: str = ""):
    if link != "":
        if link.startswith("https://"):
            embed = discord.Embed(title="Downloading song", description=link, colour=0x79A4F9)
            mess = await ctx.channel.send(content=None, embed=embed)
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "music/" + file)
            embed = discord.Embed(title="Finished downloading", description=link, colour=0x79A4F9)
            await mess.edit(content=None, embed=embed)


@bot.command()
async def find(ctx, arg: str = ""):
    files = findSong(arg)
    embed = discord.Embed(title="Song not found", description="Check if you have any typo or download the song if it isn't downloaded yet", colour=0x79A4F9)
    if len(files) == 1:
        embed = discord.Embed(title="One song found", description=files[0], colour=0x79A4F9)
    elif len(files) > 1:
        embed = discord.Embed(title=str(len(files)) + " songs found", description=listToString(files), colour=0x79A4F9)
    await ctx.channel.send(content=None, embed=embed)


@bot.command()
async def list(ctx):
    files = os.listdir("./music/")
    embed = discord.Embed(title="Current downloaded songs", description=listToString(files), colour=0x79A4F9)
    await ctx.channel.send(content=None, embed=embed)


@bot.command()
async def play(ctx, arg: str = ""):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if arg != "":
        if not voice:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
                embed = discord.Embed(title="Joined voice channel", description=channel.mention, colour=0x79A4F9)
                await ctx.channel.send(content=None, embed=embed)
            else:
                embed = discord.Embed(title="Currently not in a voice channel", description="join a voice channel or make me join", colour=0x79A4F9)
                await ctx.channel.send(content=None, embed=embed)
                return
        voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
        if voice:
            if arg.lower() == "random":
                filetoplay = os.listdir("./music/")[random.randint(0, len(os.listdir("./music/")) - 1)]
            else:
                files = findSong(arg)
                if len(files) == 1:
                    filetoplay = files[0]
                elif len(files) > 1:
                    embed = discord.Embed(title="Multiple music found", description="be more precise in the selection\n" + listToString(files), colour=0x79A4F9)
                    await ctx.channel.send(content=None, embed=embed)
                    return
                else:
                    embed = discord.Embed(title="Music not found", description="Check if you have any typo or download the song if it isn't downloaded yet", colour=0x79A4F9)
                    await ctx.channel.send(content=None, embed=embed)
                    return


            if filetoplay:
                if voice.is_playing():
                    voice.stop()
                voice.play(discord.FFmpegPCMAudio("./music/" + filetoplay))
                embed = discord.Embed(title="Now playing", description=filetoplay + " in " + ctx.guild.voice_client.channel.mention, colour=0x79A4F9)
                await ctx.channel.send(content=None, embed=embed)


    else:
        if voice:
            if voice.is_paused():
                voice.resume()
                embed = discord.Embed(title="Resumed", description="", colour=0x79A4F9)
                await ctx.channel.send(content=None, embed=embed)
            else:
                embed = discord.Embed(title="Nothing to play", description="", colour=0x79A4F9)
                await ctx.channel.send(content=None, embed=embed)

        else:
            embed = discord.Embed(title="Currently not in a voice channel", description="", colour=0x79A4F9)
            await ctx.channel.send(content=None, embed=embed)

bot.remove_command('help')

@bot.command()
async def help(ctx):
    help = ""
    for key in helpPage.keys():
        help += "**" + key + ":** " + helpPage[key] + "\n"
    embed = discord.Embed(title="Help page", description=help, colour=0x79A4F9)
    await ctx.channel.send(content=None, embed=embed)


keep_alive()
bot.run(os.getenv('token'))
