import os
import discord
from discord.ext import commands
import json
from keep_alive import keep_alive
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

bot = commands.Bot(command_prefix=">")

with open("help.json", "r") as help_file:
    helpPage = json.load(help_file)

#get a string from the message list
sortname = lambda message, init=1, end=None : " ".join(list(message[init:end]))



queue = {}

loop = 2
currentSong = {}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}



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


def playNext(ctx, currentUrl):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    print("playNext gets called")
    if voice:
        if not (voice.is_playing() or voice.is_paused()):
            if loop == 2:
                voice.play(FFmpegPCMAudio(currentUrl, **FFMPEG_OPTIONS), after=lambda e: playNext(ctx, currentUrl))
                # embed = discord.Embed(title="Now playing", description="[" + currentSong['title'] + "](https://youtu.be/" + currentSong['id'] + ")\nin " + ctx.guild.voice_client.channel.mention, colour=0x79A4F9)
                # await ctx.channel.send(content=None, embed=embed)



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
    elif ctx.author.voice:
        channel = ctx.author.voice.channel
    else:
        embed = discord.Embed(title="Could not join voice channel", description="Make sure you are connected to a voice channel", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)
        return
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    embed = discord.Embed(title="Joined voice channel", description=channel.mention, colour=0x79A4F9)
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
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        if voice.is_paused():
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
        elif voice.is_paused() or voice.is_playing():
            voice.stop()
        voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
        if voice:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(arg, download=False)
            #print(info)
            currentSong = info
            currentUrl = currentSong['url']
            #, after=await playNext(ctx)
            voice.play(FFmpegPCMAudio(currentUrl, **FFMPEG_OPTIONS), after=lambda e: playNext(ctx, currentUrl))
            embed = discord.Embed(title="Now playing", description="[" + info['title'] + "](" + arg + ")\nin " + ctx.guild.voice_client.channel.mention, colour=0x79A4F9)
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
