#imports-----------------------------------------------
from discord.ext import commands
import discord,os,xkcd,server,sys,asyncio

#variables-----------------------------------------------
ctx="xkcd "
token=os.getenv('token')
client = discord.Client()
client = commands.Bot(command_prefix=ctx,case_insensitive=True)
client.remove_command('help')
color=0x96A8C8
color = discord.Colour(color)
#functions-----------------------------------------------
async def makeComic(ctx,comic):
  title=comic.getTitle()
  alt=comic.getAltText()
  comic=comic.getImageLink()
  embed=make_embed(title=f"{title}",desc="by Randall Munroe")
  embed.set_image(url=comic)
  embed.set_footer(text=alt,icon_url="https://xkcd.com/s/919f27.ico")
  comic=await ctx.channel.send(embed=embed)
  await comic.add_reaction("🎲")
  return comic

async def makeComicNum(ctx,comic,num):
  title=comic.getTitle()
  alt=comic.getAltText()
  comic=comic.getImageLink()
  embed=make_embed(title=f"{title}",desc=f"by Randall Munroe\nComic: {num}/{xkcd.getLatestComicNum()}")
  embed.set_image(url=comic)
  embed.set_footer(text=alt,icon_url="https://xkcd.com/s/919f27.ico")
  comic=await ctx.channel.send(embed=embed)
  await comic.add_reaction("🎲")
  return comic

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
async def on_reaction_add(reaction, user):
  msg=reaction.message
  if msg.author == client.user and user.id!=718079038471798824:
    if reaction.emoji=="🎲":
      random=xkcd.getRandomComic()
      await msg.delete()
      await makeComic(msg,random)

@client.event
async def on_message(ctx):
  if "zwack" in ctx.content.lower():  
    await ctx.add_reaction("<:zwack:451912829142827008>")
  if "fire" in ctx.content.lower() or "space" in ctx.content.lower():
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
  await makeComic(ctx,latest)

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
    #integer=str(integer)
    comic=xkcd.getComic(integer)
    comic=await makeComicNum(ctx,comic,integer)
    await comic.add_reaction("◀️")
    await comic.add_reaction("▶️")
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
    while True:
      try:
        reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
        if str(reaction.emoji) == "▶️" and integer != comicNum:
          integer += 1
          await comic.delete()
          comic=xkcd.getComic(integer)
          comic=await makeComicNum(ctx,comic,integer)
          await comic.add_reaction("◀️")
          await comic.add_reaction("▶️")

        elif str(reaction.emoji) == "◀️" and integer > 0:
          integer -= 1
          await comic.delete()
          comic=xkcd.getComic(integer)
          comic=await makeComicNum(ctx,comic,integer)
          await comic.add_reaction("◀️")
          await comic.add_reaction("▶️")

        else:
          await comic.remove_reaction(reaction, user)
      except asyncio.TimeoutError:
          break
  else:
    await invalidComic(ctx,integer)

@client.command()
async def servers(ctx):
    msg = ''
    total = 0
    for i in client.guilds:
      msg += '\n' + str(i) + ' - ' + str((len(i.members))) + ' members'
      total += len(i.members)
    embed = discord.Embed(color=0x00ff00,description=f'xkcdBot is in **{str(len(client.guilds))}** servers.\nTotal members -  **{str(total)}**')
    await ctx.send(embed=embed)

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
#async def main():

server.server()
client.run(token)