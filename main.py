from discord.ext import commands
import discord,os,server
import xkcd

ctx="xkcd "
token=os.getenv('token')
client = discord.Client()
client = commands.Bot(command_prefix=ctx)
client.remove_command('help')
color = discord.Color.red()
def getrandxkcd(random):
  return 

def make_embed(title, desc):
  return discord.Embed(title=title, description=desc, color=color)

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game('xkcd help'))
  print('{0.user} is online'.format(client))

@client.event
async def on_command_error(ctx, error):
  embed = make_embed(title="Error", desc="")
  embed.add_field(name=":face_with_raised_eyebrow: ", value=error)
  await ctx.send(embed=embed)

@client.command()
async def random(ctx):
  random=xkcd.getRandomComic()
  title=random.getTitle()
  random=random.getImageLink()
  embed=make_embed(title="xkcd",desc="")
  embed.add_field(name=f"{title}",value="made by Randall Munroe")
  embed.set_image(url=random)
  await ctx.send(embed=embed)

@client.command()
async def latest(ctx):
  latest=xkcd.getLatestComic()
  title=latest.getTitle()
  latest=latest.getImageLink()
  embed=make_embed(title="xkcd",desc="")
  embed.add_field(name=f"{title}",value="made by Randall Munroe")
  embed.set_image(url=latest)
  await ctx.send(embed=embed)

@client.command()
async def comic(ctx,integer):
  try:  
    integer=int(integer)
  except ValueError:
    embed = make_embed(title="Error", desc="")
    embed.add_field(name=":face_with_raised_eyebrow: ", value=f'Comic number "{integer}" is not valid')
    await ctx.send(embed=embed)
    return
  if integer<=xkcd.getLatestComicNum():
    integer=str(integer)
    comic=xkcd.getComic(integer)
    title=comic.getTitle()
    comic=comic.getImageLink()
    embed=make_embed(title=f"xkcd",desc="")
    embed.add_field(name=f"{title}",value="made by Randall Munroe")
    embed.set_image(url=comic)
    await ctx.send(embed=embed)
  else:
    embed = make_embed(title="Error", desc="")
    embed.add_field(name=":face_with_raised_eyebrow: ", value=f'Comic number "{integer}" is not valid')
    await ctx.send(embed=embed)

@client.command()
async def help(ctx):
  embed = make_embed(title="Commands", desc="(for the new guys ;)")
  embed.add_field(name="xkcd help", value="This is the help command.")
  embed.add_field(name="xkcd random", value="This retrieves a random xkcd comic")
  embed.add_field(name="xkcd latest", value="This retrieves the latest xkcd comic")
  embed.add_field(name="xkcd comic [number]", value="This retrieves the corresponding xkcd comic to [number]")
  await ctx.send(embed=embed)


server.server()
client.run(token)