#imports-----------------------------------------------
import discord, os, xkcd, server, sys, asyncio, wikipedia as wp, re, warnings, replitdb, json, praw
from random import randrange
from bs4 import GuessedAtParserWarning
from discord.ext import commands

#variables-----------------------------------------------
defprefix="/"
token = os.getenv('token')
client = discord.Client()
client = commands.Bot(command_prefix=defprefix, case_insensitive=True)
client.remove_command('help')
color = 0x96A8C8
color = discord.Colour(color)
vaulters = [715591423633784844]
reddit = praw.Reddit(client_id=os.getenv("red"),client_secret=os.getenv("redsec"),user_agent="Nord")

#functions-----------------------------------------------
async def makeComic(ctx, comic, integer):
    comicNum = xkcd.getLatestComicNum()
    title = comic.getTitle()
    alt = comic.getAltText()
    comic = comic.getImageLink()
    embed = make_embed(
        title=f"{title}",
        desc=f"by Randall Munroe\nComic: {integer}/{comicNum}")
    embed.set_image(url=comic)
    embed.set_footer(text=alt, icon_url="https://xkcd.com/s/919f27.ico")
    comic = await ctx.channel.send(embed=embed)
    if integer > 1:
        await comic.add_reaction("◀️")
    await comic.add_reaction("🎲")
    if integer < comicNum:
        await comic.add_reaction("▶️")
    return comic


async def sendComic(ctx, comic, integer):
  comicNum = xkcd.getLatestComicNum()
  comic = await makeComic(ctx, comic, integer)

  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in ["◀️", "🎲", "▶️"]

  while True:
    try:
      reaction, user = await client.wait_for(
        "reaction_add", timeout=60, check=check)
      if str(reaction.emoji) == "▶️" and integer < comicNum and user == ctx.author:
        integer += 1
        await comic.delete()
        comic = xkcd.getComic(integer)
        comic = await makeComic(ctx, comic, integer)
      elif str(reaction.emoji) == "◀️" and integer > 1 and user == ctx.author:
        integer -= 1
        await comic.delete()
        comic = xkcd.getComic(integer)
        comic = await makeComic(ctx, comic, integer)
      elif str(reaction.emoji) == "🎲" and user == ctx.author:
        await comic.delete()
        rand=randrange(1, xkcd.getLatestComicNum())
        comic = xkcd.getComic(rand)
        comic = await makeComic(ctx, comic, rand)
    except asyncio.TimeoutError:
      break


async def makeWhatIf(ctx, whatif):
    title = whatif.getTitle()
    link = whatif.getLink()
    embed = make_embed(title=f"{title}", desc="by Randall Munroe")
    embed.add_field(name="Link", value=f'{link}')
    await ctx.send(embed=embed)


def make_embed(title, desc):
    return discord.Embed(title=title, description=desc, color=color)


#events-----------------------------------------------
@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(f"{defprefix}help"))
  print('{0.user} is online'.format(client))


@client.event
async def on_message(ctx):
  if "zwack" in ctx.content.lower():
    await ctx.add_reaction("<:zwack:451912829142827008>")
  if "fire" in ctx.content.lower() or "space" in ctx.content.lower():
    await ctx.add_reaction("⭐")
    await ctx.add_reaction("🔥")
  if ctx.content.startswith('xkcd '):
    ctx.send("This bot no longer uses this prefix the new prefix is `/`\n this message will stop appearing tommorow...so tell people")
  await client.process_commands(ctx) 
  '''
  if ctx.author.id==715591423633784844:
    db.wipe
    #print(await db.all_dict)
    #print(dict(await db.view(str(ctx.guild.id))).get("prefix"))
    #pass
  '''
  



#error-----------------------------------------------
#'''
@client.event
async def on_command_error(ctx, error):
  embed = make_embed(title="Error", desc="")
  embed.add_field(name=":face_with_raised_eyebrow: ", value=error)
  await ctx.send(embed=embed)
#'''


async def invalidComic(ctx, integer):
    embed = make_embed(title="Error", desc="")
    embed.add_field(
        name=":face_with_raised_eyebrow: ",
        value=f'Comic number "{integer}" is not valid')
    await ctx.send(embed=embed)

warnings.filterwarnings('ignore', category=GuessedAtParserWarning)

#help command----------------------------------------
@client.command()
async def help(ctx):
    embed = make_embed(title="Commands can be found on the website here: https://xkcdbot.spacefire.repl.co/",desc=" ")
    await ctx.send(embed=embed)


#xkcd commands-----------------------------------------------
@client.command(aliases=['random-xkcd',"randxkcd","rx"])
async def random_xkcd(ctx):
    integer = randrange(1, xkcd.getLatestComicNum())
    comic = xkcd.getComic(integer)
    await sendComic(ctx, comic, integer)


@client.command(aliases=['random-whatif',"randwhatif","rw"])
async def random_whatif(ctx):
    random = xkcd.getRandomWhatIf()
    await makeWhatIf(ctx, random)


@client.command(aliases=['latest-whatif',"latestwhatif","lw"])
async def latest_whatif(ctx):
    latest = xkcd.getLatestWhatIf()
    await makeWhatIf(ctx, latest)


@client.command()
async def whatif(ctx, number):
    whatif = xkcd.getWhatIf(number)
    await makeWhatIf(ctx, whatif)

@client.command()
async def comic(ctx, integer=xkcd.getLatestComicNum()):
    comicNum = xkcd.getLatestComicNum()
    try:
        integer = int(integer)
    except ValueError:
        await invalidComic(ctx, integer)
        return
    if integer <= comicNum:
        comic = xkcd.getComic(integer)
        await sendComic(ctx, comic, integer)
    else:
        await invalidComic(ctx, integer)

@client.command(aliases=['latest-xkcd',"latestxkcd","lx"])
async def latest(ctx):
    latest = xkcd.getLatestComic()
    integer = xkcd.getLatestComicNum()
    await sendComic(ctx, latest, integer)

#feedback command-----------------------------------------------
@client.command(aliases=['suggestions', 'bug', 'report'])
async def feedback(ctx, *, message=None):
    channel = client.get_channel(733608622033993749)
    location = 'https://discordapp.com/channels/' + str(
        ctx.guild.id) + '/' + str(ctx.channel.id) + '/' + str(ctx.message.id)
    if message == None or len(message) >= 2001:
        embed = make_embed(
            title="Error",
            desc=
            "Either your feedback was too long (over 2000 characters) or You did not type a feedback"
        )
        await ctx.send(embed=embed)
    else:
        embed = make_embed(
            title=f"{ctx.author} says:",
            desc=f"```{message}```\nURL: {location}\nServer: {ctx.guild}")
        await channel.send(embed=embed)
        embed = make_embed(
            title=f"Thank you for your feedback",
            desc="It has been sent to my developers")
        await ctx.send(embed=embed)

#dev commands-----------------------------------------------
@client.command(aliases=["r"])
@commands.is_owner()
async def restart(ctx):
    embed = make_embed(title=":white_check_mark:", desc="Successfully Restarted")
    await ctx.send(embed=embed)
    os.system("clear")
    os.execv(sys.executable, ['python'] + sys.argv)
    await ctx.send("succesfully restarted")

@client.command(aliases=["t"])
@commands.is_owner()
async def test(ctx,code):
    exec(code)
    await ctx.send("succesfully run")
'''
@client.command(aliases=["db"])
@commands.is_owner()
async def database(ctx,*,data):
  try:  
    data=json.loads(str(data))
    await db.set_dict(data)
    print(await db.all_dict)
    await ctx.send(f"Done, Bro")
  except Exception as e:
    await ctx.send(f"Yikes! either you or I messed up, here is what happend\n```\n{e}\n```")

@client.command(aliases=["del"])
@commands.is_owner()
async def delete(ctx,*,data):
  try:  
    await db.remove(data)
    await ctx.send(f"Done, Bro")
  except Exception as e:
    await ctx.send(f"Yikes! either you or I messed up, here is what happend\n```\n{e}\n```")
'''

@client.command(aliases=['invite link', 'invitelink'])
async def link(ctx):
    embed = make_embed(
        title="Invite Link",
        desc=
        "https://discord.com/api/oauth2/authorize?client_id=718079038471798824&permissions=0&scope=bo"
    )
    await ctx.send(embed=embed)

#info commands-----------------------------------------------
@client.command()
async def servers(ctx):
    msg = '```'
    total = 0
    for i in client.guilds:
        msg = msg + f'{i.name} {i.member_count}\n'
        total += len(i.members)
    msg = msg + '```'
    embed = make_embed(
        title=f'Nord is in **{str(len(client.guilds))}** servers', desc=msg)
    embed.add_field(name=f'Total members', value=f'{str(total)}')
    await ctx.send(embed=embed)

#wiki commands-----------------------------------------------
@client.command()
async def search(ctx, query):
    msg = '```'
    if len(wp.search(query)) == 0:
        await ctx.send("Nope- nothing like that.")
        return
    for i in wp.search(query):
        msg = msg + f'{i}\n'
    msg = msg + '```'
    embed = make_embed(title=f"Query: {query}", desc=msg)
    await ctx.send(embed=embed)


@client.command()
async def wiki(ctx, *, query=None):
    if query == None:
        await ctx.send(
            "Please type the name of the wikipedia aticle you want to see")
        return
    try:
        article = wp.page(query)
    except wp.exceptions.DisambiguationError or wp.exceptions.PageError:
        if len(wp.search(query)) > 0:
            msg = '```'
            for i in wp.search(query):
                msg = msg + f'{i}\n'
            msg = msg + '```'
            embed = make_embed(title="Your Wiki was not found here are some similar results:",desc=msg)
            await ctx.send(embed=embed)
            return
        else:
            await ctx.send(embed=make_embed(title="Lmao",desc="We could not find the wiki you were looking for or any wikis similar."))
            return
    embed = make_embed(title=article.title, desc=f"URL:{article.url}")
    sent = 10
    async with ctx.channel.typing():
      for i in range(31):
          summary = wp.summary(query, sentences=sent)
          if len(summary) >= 1024:
              sent -= 1
      sent = len(re.split(r'[.!?]+', summary)) - 1
      embed.add_field(name=f"Summary (first {sent} sentence(s)):", value=summary)
      await ctx.send(embed=embed)

#vault commands-----------------------------------------------
@client.command()
async def vault(ctx):
  author=ctx.author
  if author.id in vaulters:
    img=ctx.attachments.url
    json.dumps({img:author})
    vault=json.load(open("vault.json","r+"))
    data={img:author}
    vault.update(data)
    json.dump(vault,open("vault.json","w+"),indent=4)
  else:
    await ctx.send("You are not a Nord Vaulter")
#mod commands-----------------------------------------------
'''
@client.command(aliases=['changeprefix', 'prefixset', 'prefixchange'])
@commands.has_permissions(administrator=True)
async def setprefix(ctx, prefix):
    await db.set_dict({str(ctx.guild.id):{"prefix":prefix}})
    await ctx.send(f'Successfully changed the prefix to: **``{prefix}``**')
'''
#run-----------------------------------------------
server.server()
client.run(token)