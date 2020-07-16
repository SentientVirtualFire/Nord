#imports-----------------------------------------------
from discord.ext import commands
import discord,os,server
import xkcd

#variables-----------------------------------------------
ctx="xkcd "
token=os.getenv('token')
client = discord.Client()
client = commands.Bot(command_prefix=ctx,case_insensitive=True)
client.remove_command('help')
color = discord.Color.red()

#functions-----------------------------------------------
async def makeComic(ctx,comic):
  title=comic.getTitle()
  alt=comic.getAltText()
  comic=comic.getImageLink()
  embed=make_embed(title=f"{title}",desc="by Randall Munroe")
  embed.add_field(name="alt text",value=alt)
  embed.set_image(url=comic)
  await ctx.send(embed=embed)

async def makeWhatIf(ctx,whatif):  
  title=whatif.getTitle()
  link=whatif.getLink()
  embed = make_embed(title=f"{title}", desc="by Randall Munroe")
  embed.add_field(name="Link", value=f'{link}')
  await ctx.send(embed=embed)

def make_embed(title, desc):
  return discord.Embed(title=title, description=desc, color=color)

#ready-----------------------------------------------
@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game('xkcd help'))
  print('{0.user} is online'.format(client))

#error-----------------------------------------------
@client.event
async def on_command_error(ctx, error):
  embed = make_embed(title="Error", desc="")
  embed.add_field(name=":face_with_raised_eyebrow: ", value=error)
  await ctx.send(embed=embed)
  
async def invalidComic(ctx,integer):  
  embed = make_embed(title="Error", desc="")
  embed.add_field(name=":face_with_raised_eyebrow: ", value=f'Comic number "{integer}" is not valid')
  await ctx.send(embed=embed)

#commands-----------------------------------------------
@client.command()
async def random(ctx):
  random=xkcd.getRandomComic()
  await makeComic(ctx,random)

@client.command(aliases=['random-whatif'])
async def random_whatif(ctx):
  random=xkcd.getRandomWhatIf()
  await makeWhatIf(ctx,random)  

@client.command(aliases=['latest-whatif'])
async def latest_whatif(ctx):
  latest=xkcd.getLatestWhatIf()
  await makeWhatIf(ctx,latest)  

@client.command()
async def whatif(ctx,number):
  whatif=xkcd.getWhatIf(number)
  await makeWhatIf(ctx,whatif)  

@client.command()
async def latest(ctx):
  latest=xkcd.getLatestComic()
  await makeComic(ctx,latest)

@client.command(aliases=['invite link','invitelink'])
async def link(ctx):
  embed = make_embed(title="Invite Link", desc="https://discord.com/api/oauth2/authorize?client_id=718079038471798824&permissions=0&scope=bo")
  await ctx.send(embed=embed)

@client.command()
async def comic(ctx,integer):
  try:  
    integer=int(integer)
  except ValueError:
    await invalidComic(ctx,integer)
    return
  if integer<=xkcd.getLatestComicNum():
    integer=str(integer)
    comic=xkcd.getComic(integer)
    await makeComic(ctx,comic)
    await invalidComic(ctx,integer)

#help command----------------------------------------
@client.command()
async def help(ctx):
  embed = make_embed(title="Commands", desc="These are the xkcdBot commands. All commands are case-insensitive.")
  embed.add_field(name="xkcd help", value="This is the help command")
  embed.add_field(name="xkcd random", value="This retrieves a random xkcd comic")
  embed.add_field(name="xkcd latest", value="This retrieves the latest xkcd comic")
  embed.add_field(name="xkcd comic [number]", value="This retrieves the corresponding xkcd comic to [number]")
  embed.add_field(name="xkcd random-whatif", value="This retrieves a random WhatIf link")
  embed.add_field(name="xkcd latest-whatif", value="This retrieves the latest WhatIf link")
  embed.add_field(name="xkcd whatif [number]", value="This retrieves the corresponding Whatif to [number]")
  await ctx.send(embed=embed)


#run-----------------------------------------------
server.server()
client.run(token)