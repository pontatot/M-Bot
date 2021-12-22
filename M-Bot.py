import os
import discord
from discord.ext import commands
import json
from keep_alive import keep_alive
from discord import FFmpegPCMAudio
import youtube_dl
from restartidk import restartidk
import random

bot = commands.Bot(command_prefix=">")

with open("help.json", "r") as help_file:
    helpPage = json.load(help_file)

#get a string from the message list
sortname = lambda message, init=1, end=None : " ".join(list(message[init:end]))


songQueue = {}
currentPos = {}

loopType = {}
YDL_OPTIONS = {'default_search': 'auto', 'format': 'bestaudio/best', 'noplaylist': 'True', 'nocheckcertificate': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}



#extract id from discord mentions
def getid(message):
    try:
        return int(message.replace("<", "").replace("#", "").replace("@", "").replace("!", "").replace("&", "").replace(">", ""))
    except:
        return None


def mkEmbed(title = "", desc = ""):
    return discord.Embed(title=title, description=desc, colour=0x79A4F9)


def playNext(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    global currentPos
    if voice:
        if not (voice.is_playing() or voice.is_paused()):
            if loopType[str(ctx.guild.id)] == 2:
                voice.play(FFmpegPCMAudio(songQueue[str(ctx.guild.id)][currentPos[str(ctx.guild.id)]][2], **FFMPEG_OPTIONS), after=lambda e: playNext(ctx))
            elif loopType[str(ctx.guild.id)] == 1:
                currentPos[str(ctx.guild.id)] += 1
                if currentPos[str(ctx.guild.id)] >= len(songQueue[str(ctx.guild.id)]):
                    currentPos[str(ctx.guild.id)] = 0
                voice.play(FFmpegPCMAudio(songQueue[str(ctx.guild.id)][currentPos[str(ctx.guild.id)]][2], **FFMPEG_OPTIONS), after=lambda e: playNext(ctx))



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
        global currentPos
        try:
            songQueue[str(message.guild.id)] = songQueue[str(message.guild.id)]
            loopType[str(message.guild.id)] = loopType[str(message.guild.id)]
            currentPos[str(message.guild.id)]
        except:
            songQueue[str(message.guild.id)] = []
            loopType[str(message.guild.id)] = 1
            currentPos[str(message.guild.id)] = 0
    except:
        return







    await bot.process_commands(message)





@bot.command()
async def ping(ctx):
    mention = discord.AllowedMentions(replied_user=False)
    await ctx.reply(content=None, embed=mkEmbed("Pong", f"{round(bot.latency * 1000)} ms"), allowed_mentions=mention)


@bot.command()
async def join(ctx, id: int = 0):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if id != 0:
        channel = bot.get_channel(id)
    elif ctx.author.voice:
        channel = ctx.author.voice.channel
    else:
        await ctx.channel.send(content=None, embed=mkEmbed("Could not join voice channel", "Make sure you are connected to a voice channel"))
        return
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await ctx.channel.send(content=None, embed=mkEmbed("Joined voice channel", channel.mention))


@bot.command()
async def leave(ctx):
    voice = ctx.guild.voice_client
    if voice:
        global loopType
        loopType[str(ctx.guild.id)] = 0
        global songQueue
        songQueue[str(ctx.guild.id)] = []
        global currentPos
        currentPos[str(ctx.guild.id)] = 0
        voice.stop()
        channel = ctx.guild.voice_client
        await channel.disconnect()
        await ctx.channel.send(content=None, embed=mkEmbed("Left voice channel", channel.channel.mention))
    else:
        await ctx.channel.send(content=None, embed=mkEmbed("Currently not in a voice channel"))


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        if voice.is_playing():
            voice.pause()
            await ctx.channel.send(content=None, embed=mkEmbed("Paused"))
        elif voice.is_paused():
            voice.resume()
            await ctx.channel.send(content=None, embed=mkEmbed("Resumed"))
        else:
            await ctx.channel.send(content=None, embed=mkEmbed("Not playing audio"))
    else:
        await ctx.channel.send(content=None, embed=mkEmbed("Currently not in a voice channel"))


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        if voice.is_paused():
            voice.resume()
            await ctx.channel.send(content=None, embed=mkEmbed("Resumed"))
        else:
            await ctx.channel.send(content=None, embed=mkEmbed("Not playing audio"))
    else:
        await ctx.channel.send(content=None, embed=mkEmbed("Currently not in a voice channel"))


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        global loopType
        loopType[str(ctx.guild.id)] = 0
        global songQueue
        songQueue[str(ctx.guild.id)] = []
        global currentPos
        currentPos[str(ctx.guild.id)] = 0
        voice.stop()
        await ctx.channel.send(content=None, embed=mkEmbed("Stopped"))
    else:
        await ctx.channel.send(content=None, embed=mkEmbed("Currently not in a voice channel"))


@bot.command()
async def play(ctx, *, arg: str = ""):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if arg != "":
        voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(arg, download=False)
        if not voice:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
                await ctx.channel.send(content=None, embed=mkEmbed("Joined voice channel", channel.mention))
            else:
                await ctx.channel.send(content=None, embed=mkEmbed("Currently not in a voice channel", "join a voice channel or make me join"))
                return
        global songQueue
        try:
            songQueue[str(ctx.guild.id)].append([info['title'], "https://youtu.be/" + info['id'], info['url']])
            embed = mkEmbed("Queued", "[" + info['title'] + "](https://youtu.be/" + info['id'] + ")")
            embed.set_thumbnail(url=info["thumbnails"][0])
            await ctx.channel.send(content=None, embed=embed)
            playNext(ctx)
        except:
            result = [""]
            index = 0
            for i in range(len(info['entries'])):
                localinfo = info['entries'][i]
                songQueue[str(ctx.guild.id)].append([localinfo['title'], "https://youtu.be/" + localinfo['id'], localinfo['url']])
                if len(result[index]) >= 5500:
                    index += 1
                    result.append("")
                result[index] += "-Queued [" + localinfo['title'] + "](https://youtu.be/" + localinfo['id'] + ")\n"
            for i in result:
                embed = mkEmbed("", i)
                await ctx.channel.send(content=None, embed=embed)
            playNext(ctx)
        



    else:
        if voice:
            if voice.is_paused():
                voice.resume()
                await ctx.channel.send(content=None, embed=mkEmbed("Resumed"))
            else:
                await ctx.channel.send(content=None, embed=mkEmbed("Nothing to play"))

        else:
            await ctx.channel.send(content=None, embed=mkEmbed("Currently not in a voice channel"))

bot.remove_command('help')

@bot.command()
async def help(ctx):
    help = ""
    for key in helpPage.keys():
        help += "**" + key + ":** " + helpPage[key] + "\n"
    await ctx.channel.send(content=None, embed=mkEmbed("Help page", help))


@bot.command()
async def queue(ctx):
    queue = ""
    if len(songQueue[str(ctx.guild.id)]) > 0:
        for i in range(len(songQueue[str(ctx.guild.id)])):
            if i == currentPos[str(ctx.guild.id)]:
                queue += "**__" + str(i + 1) + ") [" + songQueue[str(ctx.guild.id)][i][0] + "](" + songQueue[str(ctx.guild.id)][i][1] + ")__**\n"
            else:
                queue += str(i + 1) + ") [" + songQueue[str(ctx.guild.id)][i][0] + "](" + songQueue[str(ctx.guild.id)][i][1] + ")\n"
    else:
        queue = "Queue is empty"
    await ctx.channel.send(content=None, embed=mkEmbed("Current queue", queue))


@bot.command()
async def skip(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        pos = currentPos[str(ctx.guild.id)] + 1
        if pos >= len(songQueue[str(ctx.guild.id)]):
            pos = 0
        voice.stop()
        await ctx.channel.send(content=None, embed=mkEmbed("Skipped", "[" + songQueue[str(ctx.guild.id)][pos][0] + "](" + songQueue[str(ctx.guild.id)][pos][1] + ")\n"))

@bot.command()
async def previous(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        global currentPos
        currentPos[str(ctx.guild.id)] -= 2
        if currentPos[str(ctx.guild.id)] < 0:
            currentPos[str(ctx.guild.id)] = len(songQueue[str(ctx.guild.id)]) + currentPos[str(ctx.guild.id)]
        pos = currentPos[str(ctx.guild.id)] + 1
        if pos >= len(songQueue[str(ctx.guild.id)]):
            pos = 0
        voice.stop()
        await ctx.channel.send(content=None, embed=mkEmbed("Previous", "[" + songQueue[str(ctx.guild.id)][pos][0] + "](" + songQueue[str(ctx.guild.id)][pos][1] + ")\n"))

@bot.command()
async def loop(ctx):
    global loopType
    loopType[str(ctx.guild.id)] += 1
    if loopType[str(ctx.guild.id)] >= 3:
        loopType[str(ctx.guild.id)] = 0
    thing = ["not looping", "loop queue", "loop current song"]
    await ctx.channel.send(content=None, embed=mkEmbed("Changed loop", thing[loopType[str(ctx.guild.id)]]))


@bot.command()
async def remove(ctx, arg: int = 0):
    global songQueue
    song = songQueue[str(ctx.guild.id)][arg - 1]
    songQueue[str(ctx.guild.id)].pop(arg - 1)
    global currentPos
    if arg < currentPos[str(ctx.guild.id)]:
        currentPos[str(ctx.guild.id)] -= 1
        if currentPos[str(ctx.guild.id)] < 0:
            currentPos[str(ctx.guild.id)] = len(songQueue[str(ctx.guild.id)]) + currentPos[str(ctx.guild.id)]
    await ctx.channel.send(content=None, embed=mkEmbed("Removed", "[" + song[0] + "](" + song[1] + ")\n"))

@bot.command()
async def jump(ctx, arg: int = currentPos[str(ctx.guild.id)] + 1):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.channel.guild)
    if voice:
        global currentPos
        currentPos[str(ctx.guild.id)] = arg - 2
        if currentPos[str(ctx.guild.id)] >= len(songQueue[str(ctx.guild.id)]):
            currentPos[str(ctx.guild.id)] = 0
        if currentPos[str(ctx.guild.id)] < 0:
            currentPos[str(ctx.guild.id)] = len(songQueue[str(ctx.guild.id)]) + currentPos[str(ctx.guild.id)]
        pos = currentPos[str(ctx.guild.id)] + 1
        if pos >= len(songQueue[str(ctx.guild.id)]):
            pos = 0
        voice.stop()
        await ctx.channel.send(content=None, embed=mkEmbed("Jumped to song" + str(arg), "[" + songQueue[str(ctx.guild.id)][pos][0] + "](" + songQueue[str(ctx.guild.id)][pos][1] + ")\n"))

@bot.command()
async def restart(ctx):
    restartidk()

@bot.command()
async def fixplay(ctx):
    global currentPos
    currentPos[str(ctx.guild.id)] = 0
    playNext(ctx)

@bot.command()
async def shuffle(ctx):
    global songQueue
    random.shuffle(songQueue[str(ctx.guild.id)])
    await ctx.channel.send(content=None, embed=mkEmbed("Shuffled the queue"))

keep_alive()
bot.run(os.getenv('token'))