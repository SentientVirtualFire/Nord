#imports-----------------------------------------------
import discord,os,xkcd,server,sys,asyncio,wikipedia as wp,re,warnings
from random import randrange
from bs4 import GuessedAtParserWarning
from discord.ext import commands

#variables-----------------------------------------------
ctx="xkcd "
token=os.getenv('token')
client = discord.Client()
client = commands.Bot(command_prefix=ctx,case_insensitive=True)
client.remove_command('help')
color=0x96A8C8
color = discord.Colour(color)

#functions-----------------------------------------------
async def makeComic(ctx,comic,integer):
  comicNum=xkcd.getLatestComicNum()
  title=comic.getTitle()
  alt=comic.getAltText()
  comic=comic.getImageLink()
  embed=make_embed(title=f"{title}",desc=f"by Randall Munroe\nComic: {integer}/{comicNum}")
  embed.set_image(url=comic)
  embed.set_footer(text=alt,icon_url="https://xkcd.com/s/919f27.ico")
  comic=await ctx.channel.send(embed=embed)
  if integer>1:
    await comic.add_reaction("◀️")
  await comic.add_reaction("🎲")
  if integer<comicNum:
    await comic.add_reaction("▶️")
  return comic

async def sendComic(ctx,comic,integer):
  comicNum=xkcd.getLatestComicNum()
  comic=await  makeComic(ctx,comic,integer)
  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
  while True:
    try:
      reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
      if str(reaction.emoji) == "▶️" and integer < comicNum and user == ctx.author:
        integer += 1
        await comic.delete()
        comic=xkcd.getComic(integer)
        comic=await  makeComic(ctx,comic,integer)
      elif str(reaction.emoji) == "◀️" and integer > 1 and user == ctx.author:
        integer -= 1
        await comic.delete()
        comic=xkcd.getComic(integer)
        comic=await  makeComic(ctx,comic,integer)
      elif str(reaction.emoji) == "🎲" and user == ctx.author:
        await comic.delete()
        comic=xkcd.getComic(integer)
        comic=await  makeComic(ctx,comic,integer)
    except asyncio.TimeoutError:
      break

async def makeWhatIf(ctx,whatif):  
  title=whatif.getTitle()
  link=whatif.getLink()
  embed = make_embed(title=f"{title}", desc="by Randall Munroe")
  embed.add_field(name="Link", value=f'{link}')
  await ctx.send(embed=embed)

def make_embed(title, desc):
  return discord.Embed(title=title, description=desc, color=color)

#events-----------------------------------------------
@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game('xkcd help'))
  print('{0.user} is online'.format(client))

@client.event
async def on_message(ctx):
  if "zwack" in ctx.content.lower():  
    await ctx.add_reaction("<:zwack:451912829142827008>")
  if "fire" in ctx.content.lower() or "space" in ctx.content.lower():
    await ctx.add_reaction("⭐") 
    await ctx.add_reaction("🔥") 
  await client.process_commands(ctx)
#error-----------------------------------------------
'''
@client.event
async def on_command_error(ctx, error):
  embed = make_embed(title="Error", desc="")
  embed.add_field(name=":face_with_raised_eyebrow: ", value=error)
  await ctx.send(embed=embed)
'''
async def invalidComic(ctx,integer):  
  embed = make_embed(title="Error", desc="")
  embed.add_field(name=":face_with_raised_eyebrow: ", value=f'Comic number "{integer}" is not valid')
  await ctx.send(embed=embed)

async def invalidWiki(ctx,integer):  
  embed = make_embed(title="Error", desc="")
  embed.add_field(name=":face_with_raised_eyebrow: ", value=f'The Wikipedia page "{integer}" does not exist')
  await ctx.send(embed=embed)
warnings.filterwarnings('ignore', category=GuessedAtParserWarning)
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

#commands-----------------------------------------------
@client.command()
async def random(ctx):
  integer=randrange(1,xkcd.getLatestComicNum())
  comic=xkcd.getComic(integer)
  await sendComic(ctx,comic,integer)

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

@client.command(aliases=['suggestions','bug','report'])
async def feedback(ctx,*,message=None):
  channel=client.get_channel(733608622033993749)
  location = 'https://discordapp.com/channels/'+str(ctx.guild.id)+'/'+str(ctx.channel.id)+'/'+str(ctx.message.id)
  if message==None or len(message)>=2001:
    embed=make_embed(title="Error",desc="Either your feedback was too long (over 2000 characters) or You did not type a feedback")
    await ctx.send(embed=embed) 
  else:
    embed=make_embed(title=f"{ctx.author} says:",desc=f"```{message}```\nURL: {location}\nServer: {ctx.guild}")
    await channel.send(embed=embed)
    embed=make_embed(title=f"Thank you for your feedback",desc="It has been sent to my developers")
    await ctx.send(embed=embed)

@client.command()
async def latest(ctx):
  latest=xkcd.getLatestComic()
  integer=xkcd.getLatestComicNum()
  await sendComic(ctx,latest,integer)

@client.command(aliases=["r"])
@commands.is_owner()
async def restart(ctx):
  embed=make_embed(title=":white_check_mark:",desc="Successfully Restarted")
  await ctx.send(embed=embed)
  os.system("clear")
  os.execv(sys.executable, ['python'] + sys.argv)
  await ctx.send("succesfully restarted")

@client.command(aliases=['invite link','invitelink'])
async def link(ctx):
  embed = make_embed(title="Invite Link", desc="https://discord.com/api/oauth2/authorize?client_id=718079038471798824&permissions=0&scope=bo")
  await ctx.send(embed=embed)


@client.command()
async def comic(ctx,integer=xkcd.getLatestComicNum()):
  comicNum=xkcd.getLatestComicNum()
  try:  
    integer=int(integer)
  except ValueError:
    await invalidComic(ctx,integer)
    return
  if integer<=comicNum:
    comic=xkcd.getComic(integer)
    await sendComic(ctx,comic,integer)
  else:
    await invalidComic(ctx,integer)

@client.command()
async def servers(ctx):
    msg = '```'
    total = 0
    for i in client.guilds:
      msg=msg+f'{i.name} {i.member_count}\n'
      total += len(i.members)
    msg=msg+'```'
    embed = make_embed(title=f'xkcdBot is in **{str(len(client.guilds))}** servers',desc=msg)  
    embed.add_field(name=f'Total members',value=f'{str(total)}')
    await ctx.send(embed=embed)

@client.command()
async def search(ctx,query):
  msg = '```'
  if len(wp.search(query))==0:
    await ctx.send("Nope- nothing like that.")
    return
  for i in wp.search(query):
    msg=msg+f'{i}\n'
  msg=msg+'```'
  embed=make_embed(title=f"Query: {query}",desc=msg)
  await ctx.send(embed=embed)

@client.command()
async def wiki(ctx,*,query=None):
    if query==None:
      await ctx.send("Please type the name of the wikipedia aticle you want to see")
      return
    try:
      article=wp.page(query)
    except wp.exceptions.DisambiguationError or wp.exceptions.PageError:
      if len(wp.search(query))>0:
        msg = '```'
        for i in wp.search(query):
          msg=msg+f'{i}\n'
        msg=msg+'```'
        embed=make_embed(title="Your Wiki was not found here are some similar results:",desc=msg)
        await ctx.send(embed=embed)
        return
      else:
        await ctx.send(embed=make_embed(title="Lmao",desc="We could not find the wiki you were looking for or any wikis similar."))
        return
    embed=make_embed(title=article.title,desc=f"URL:{article.url}")
    sent=10
    for i in range(31):  
      summary=wp.summary(query,sentences=sent)
      if len(summary)>=1024:
        sent-=1
    sent=len(re.split(r'[.!?]+', summary))-1
    embed.add_field(name=f"Summary (first {sent} sentence(s)):",value=summary)
    await ctx.send(embed=embed)

#run-----------------------------------------------
server.server()
client.run(token)