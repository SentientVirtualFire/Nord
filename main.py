#imports-----------------------------------------------
import discord, os, xkcd, sys, asyncio, wikipedia as wp, re, warnings, praw, json, server
from random import randrange,choice
from bs4 import GuessedAtParserWarning
from discord.ext import commands
'''server,'''
#variables-----------------------------------------------
defprefix="["
token = os.getenv('token')
client = commands.Bot(command_prefix=defprefix, case_insensitive=True)
client.remove_command('help')
color = 0x96A8C8
color = discord.Colour(color)
vaulters = [715591423633784844]
reddit = praw.Reddit(client_id=os.getenv("red"),client_secret=os.getenv("redsec"),user_agent="Nord by /u/SpaceFire314")
global seen
seen = {}
reddit_nono=[437048931827056642]
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
    embed.set_footer(text=alt)
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
  print(f'{client.user} is online')



@client.event
async def on_message(ctx):
  if "zwack" in ctx.content.lower():
    await ctx.add_reaction("<:zwack:451912829142827008>")
  if "fire" in ctx.content.lower() or "space" in ctx.content.lower():
    await ctx.add_reaction("⭐")
    await ctx.add_reaction("🔥")
  '''
  if ctx.author.id==671394498940633108:
    while True:
      channel = await ctx.author.create_dm()
      await channel.send("SHREK")
  '''
  await client.process_commands(ctx) 
  



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
@client.command(name="help", aliases=['h'], description="Returns all commands available.")
async def help(ctx):
    single = True
    if (len(ctx.message.content.split(" ")) > 1):
        single = False
    if (single):
        embed = discord.Embed(
            title="Help", description="prefix= `[`", color=color)
        for command in client.commands:
            view = True
#'''
            # hide dev command(s)
            if str(command) in ['restart','test']:
              view = False
#'''
            if (view == True):
              if (command.description == ''):
                command.description = 'No description'
              commands = f"( {command}"
              yes = False
              for i in command.aliases:
                  yes = True
                  commands += f" | {i}"
              if (yes):
                  commands += " )"
              else:
                  commands = commands[2:]
              embed.add_field(name=commands,value=str(command.description),inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Help per command soon")


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

@client.command(aliases=['invite link', 'invitelink'])
async def link(ctx):
    embed = make_embed(title="Invite Link",desc="https://discord.com/api/oauth2/authorize?client_id=718079038471798824&permissions=0&scope=bo")
    await ctx.send(embed=embed)

#info commands-----------------------------------------------
@client.command()
async def servers(ctx):
    msg = '```'
    total = 0
    for i in client.guilds:
      total += i.member_count
    for i in client.guilds:
        msg = msg + f'{i.name} {round((i.member_count/total)*100,2)}%\n'
        #total += len(i.members)
    msg = msg + '```'
    embed = make_embed(
        title=f'Nord is in **{str(len(client.guilds))}** servers', desc=msg)
    embed.add_field(name=f'Total members', value=f'{str(total)}')
    await ctx.send(embed=embed)

@client.command(name="prof", description="Get the info from the mentioned user.")
async def prof(ctx,*,member:discord.Member=None):
  author=ctx.author
  if member==None:  
    user=str(author)
    avatar=str(author.avatar_url)
    userid=str(author.id)
    join=str(author.joined_at)
    nick=str(author.nick)
    rolesraw=[role.mention for role in author.roles]
    del rolesraw[0]
    roles=''.join(rolesraw)
    created=str(author.created_at)
  else:
    user=str(member)
    userid=str(member.id)
    avatar=str(member.avatar_url)
    join=str(member.joined_at)
    nick=str(member.nick)
    rolesraw=[role.mention for role in member.roles]
    del rolesraw[0]
    
    roles=''.join(rolesraw)
    created=str(member.created_at)
  embed=make_embed(title=user,desc="")
  embed.add_field(name="Id",value=userid)
  embed.add_field(name=f"Joined {ctx.guild}",value=join)
  embed.add_field(name="Nickname",value=nick)
  embed.add_field(name="Roles",value=roles)
  embed.add_field(name="Created Acount",value=created)
  embed.set_thumbnail(url=avatar)
  await ctx.send(embed=embed)

@client.command(name="ping", description="Check the ping of the bot.")
async def ping(ctx):
  await ctx.send(f"Pong!\n`{round(client.latency * 1000)}ms`")
#wiki commands-----------------------------------------------
@client.command(aliases=["sw"])
async def search_wiki(ctx, query):
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
  async with ctx.channel.typing():  
    if query == None:
      await ctx.send("Please type the name of the wikipedia aticle you want to see")
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
    for i in range(31):
      summary = wp.summary(query, sentences=sent)
      if len(summary) >= 1024:
          sent -= 1
    sent = len(re.split(r'[.!?]+', summary)) - 1
    embed.add_field(name=f"Summary (first {sent} sentence(s)):", value=summary)
    await ctx.send(embed=embed)

#reddit commands----------------------------------------
@client.command()
async def meme(ctx):
  if int(ctx.guild.id) not in reddit_nono or ctx.channel.is_nsfw():
    global seen
    subreddit=choice(["dankmemes","memes","PrequelMemes","terriblefacebookmemes","Discordmemes","Catmemes","WhitePeopleTwitter"])
    posts=reddit.subreddit(subreddit).hot(limit=20)
    if str(ctx.author) in seen:
      if len(seen[str(ctx.author)])>25:
        seen[str(ctx.author)]=[]
    for x in posts:
      try:
        if not x.over_18 and not x.stickied and x not in seen[str(ctx.author)]:
          submission = x
          seen[str(ctx.author)].append(submission.id)
          break
      except KeyError:
        if not x.over_18 and not x.stickied:
          submission = x
          submission = x
          seen[str(ctx.author)]=[submission.id]
          break
    embed=discord.Embed(title=submission.title,colour=color,url=submission.shortlink,description="")
    embed.set_image(url=submission.url)
    embed.set_footer(text=f"👍 {submission.ups}\n💬 {submission.num_comments}\n Thanks to u/{submission.author.name} for providing this meme at r/{subreddit}")
    await ctx.send(embed=embed)
  else:
    embed = make_embed(title=f"This Command may produce nsfw results which are not allowed here",desc="Server where it is allowed: https://discord.gg/nDjT5nR")
    embed.set_image(url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fpreview.redd.it%2Fssb6bwxqm4311.jpg%3Fwidth%3D1024%26auto%3Dwebp%26s%3D1ea83647f151bd5f94695f2907ad39f4d1d49c42&f=1&nofb=1")
    await ctx.send(embed=embed)

@client.command(aliases=["sr"])
async def search_reddit(ctx,*,query):
  if ctx.guild.id not in reddit_nono or ctx.channel.is_nsfw():
    search=reddit.subreddits.search_by_name(query, include_nsfw=False)
    msg = '```'
    if len(search) == 0:
        await ctx.send("Nope- nothing like that.")
        return
    for i in search:
        msg = msg + f'r/{i}\n'
    msg = msg + '```'
    embed = make_embed(title=f"Query: {query}", desc=msg)
    await ctx.send(embed=embed)
  else:
    embed = make_embed(title=f"This Command may produce nsfw results which are not allowed here",desc="Server where it is allowed: https://discord.gg/nDjT5nR")
    embed.set_image(url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fpreview.redd.it%2Fssb6bwxqm4311.jpg%3Fwidth%3D1024%26auto%3Dwebp%26s%3D1ea83647f151bd5f94695f2907ad39f4d1d49c42&f=1&nofb=1")
    await ctx.send(embed=embed)

#run-----------------------------------------------
server.server()
client.run(token)