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


songQueue = {}
currentPos = 0

loopType = {}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}



#extract id from discord mentions
def getid(message):
    try:
        return int(message.replace("<", "").replace("#", "").replace("@", "").replace("!", "").replace("&", "").replace(">", ""))
    except:
        return None


def playNext(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    global currentPos
    if voice:
        if not (voice.is_playing() or voice.is_paused()):
            if loopType[str(ctx.guild.id)] == 2:
                voice.play(FFmpegPCMAudio(songQueue[str(ctx.guild.id)][currentPos][2], **FFMPEG_OPTIONS), after=lambda e: playNext(ctx))
            elif loopType[str(ctx.guild.id)] == 1:
                currentPos += 1
                if currentPos >= len(songQueue[str(ctx.guild.id)]):
                    currentPos = 0
                voice.play(FFmpegPCMAudio(songQueue[str(ctx.guild.id)][currentPos][2], **FFMPEG_OPTIONS), after=lambda e: playNext(ctx))



@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    try:
      print(message.author.name + "> " + message.content)
      messlist = list(message.content.split(" "))
      global songQueue
      global loopType
      try:
          songQueue[str(message.guild.id)] = songQueue[str(message.guild.id)]
          loopType[str(message.guild.id)] = loopType[str(message.guild.id)]
      except:
          songQueue[str(message.guild.id)] = []
          loopType[str(message.guild.id)] = 1
    except:
      return







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
    voice = ctx.guild.voice_client
    if voice:
        global loopType
        loopType[str(ctx.guild.id)] = 0
        global songQueue
        songQueue[str(ctx.guild.id)] = []
        global currentPos
        currentPos = 0
        voice.stop()
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
        global loopType
        loopType[str(ctx.guild.id)] = 0
        global songQueue
        songQueue[str(ctx.guild.id)] = []
        global currentPos
        currentPos = 0
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
        voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
        if voice:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(arg, download=False)
            songQueue[str(ctx.guild.id)].append([info['title'], "https://youtu.be/" + info['id'], info['url']])
            playNext(ctx)
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


@bot.command()
async def queue(ctx):
    queue = ""
    if len(songQueue[str(ctx.guild.id)]) > 0:
        for i in range(len(songQueue[str(ctx.guild.id)])):
            if i == currentPos:
                queue += "**__" + str(i + 1) + ") [" + songQueue[str(ctx.guild.id)][i][0] + "](" + songQueue[str(ctx.guild.id)][i][1] + ")__**\n"
            else:
                queue += str(i + 1) + ") [" + songQueue[str(ctx.guild.id)][i][0] + "](" + songQueue[str(ctx.guild.id)][i][1] + ")\n"
    else:
        queue = "Queue is empty"
    embed = discord.Embed(title="Current queue", description=queue, colour=0x79A4F9)
    await ctx.channel.send(content=None, embed=embed)


@bot.command()
async def skip(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        pos = currentPos + 1
        if pos >= len(songQueue[str(ctx.guild.id)]):
            pos = 0
        voice.stop()
        embed = discord.Embed(title="Skipped", description="[" + songQueue[str(ctx.guild.id)][pos][0] + "](" + songQueue[str(ctx.guild.id)][pos][1] + ")\n", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)

@bot.command()
async def previous(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        global currentPos
        currentPos -= 2
        if currentPos < 0:
            currentPos = len(songQueue[str(ctx.guild.id)]) + currentPos
        pos = currentPos + 1
        if pos >= len(songQueue[str(ctx.guild.id)]):
            pos = 0
        voice.stop()
        embed = discord.Embed(title="Previous", description="[" + songQueue[str(ctx.guild.id)][pos][0] + "](" + songQueue[str(ctx.guild.id)][pos][1] + ")\n", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)

@bot.command()
async def loop(ctx):
    global loopType
    loopType[str(ctx.guild.id)] += 1
    if loopType[str(ctx.guild.id)] >= 3:
        loopType[str(ctx.guild.id)] = 0
    thing = ["not looping", "loop queue", "loop current song"]
    embed = discord.Embed(title="Changed loop", description=thing[loopType[str(ctx.guild.id)]], colour=0x79A4F9)
    await ctx.channel.send(content=None, embed=embed)


@bot.command()
async def remove(ctx, arg: int = currentPos + 1):
    global songQueue
    song = songQueue[str(ctx.guild.id)][arg - 1]
    songQueue[str(ctx.guild.id)].pop(arg - 1)
    global currentPos
    if arg < currentPos:
        currentPos -= 1
        if currentPos < 0:
            currentPos = len(songQueue[str(ctx.guild.id)]) + currentPos
    embed = discord.Embed(title="Removed", description="[" + song[0] + "](" + song[1] + ")\n", colour=0x79A4F9)
    await ctx.channel.send(content=None, embed=embed)

@bot.command()
async def jump(ctx, arg: int = currentPos + 1):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        global currentPos
        currentPos = arg - 2
        if currentPos >= len(songQueue[str(ctx.guild.id)]):
            currentPos = 0
        if currentPos < 0:
            currentPos = len(songQueue[str(ctx.guild.id)]) + currentPos
        pos = currentPos + 1
        if pos >= len(songQueue[str(ctx.guild.id)]):
            pos = 0
        voice.stop()
        embed = discord.Embed(title="Jumped to song " + str(arg), description="[" + songQueue[str(ctx.guild.id)][pos][0] + "](" + songQueue[str(ctx.guild.id)][pos][1] + ")\n", colour=0x79A4F9)
        await ctx.channel.send(content=None, embed=embed)



keep_alive()
bot.run(os.getenv('token'))