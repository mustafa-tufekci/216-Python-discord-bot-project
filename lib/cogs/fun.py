from os import name
import random
import requests
from typing import Optional
from discord.ext.commands import Cog
from discord.ext.commands import command, cooldown
from discord import Member, embeds
from discord import Embed
from typing import Optional
from random import choice, randint
from aiohttp import request
from discord.ext.commands.cooldowns import BucketType
 
class Fun(Cog):
    """
    Fun cog contains the following commands such as dice (6 sided), coin etc. 
    """
    def __init__(self, bot):
        self.bot = bot

    # hidden true olursa default help komutunda bu komut görünmez
    @command(name="hello", aliases=["hi"])
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello','Hi','Hey','Hiya'))} {ctx.author.mention}!")

    # @command(brief="Give a random number between 1 and 100")
    # async def roll(self, ctx):
    #     n = random.randrange(1, 101)
    #     await ctx.send(n)


    @command(brief="Either Heads or Tails")
    async def coin(self, ctx):
        """
        `!coin` -> Toss a coin and see if it comes up heads or tails.
        """
        n = random.randint(0, 1)
        await ctx.send("Heads" if n == 1 else "Tails")


    # @command(brief="Random number between 1 and 6")
    # async def dice(self, ctx):
    #     n = random.randrange(1, 6)
    #     await ctx.send(n)

    @command(name="dice", aliases=["roll"])
    async def roll_dice(self, ctx, die_string: str):
        """
        `dice|roll <roll_number>d<dice_side_number>` -> This command creates a dice with as many faces as you want and you can choose how many times you can roll, and prints the sum of the dices rolled.
        """
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

        else:
            await ctx.send("I can't roll that many dice. Please try a lower number.")

    @command(name="slap", aliases=["hit"])
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
        await ctx.send(f"{ctx.author.nick} slapped {member.mention} for {reason}!")
    
    @command(name="echo", aliases=["say"])
    async def echo_message(self, ctx, *, message):
        """
        `echo|say <message>` -> bot writes the same message as you typed
        """
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="fact") # ``rate``, ``per``, and ``type``
    @cooldown(1, 15, BucketType.guild)  # command cooldown (kaç yazma hakkı var, kaç sn sonra yazabilir, kimleri kapsar)
    async def animal_fact(self, ctx, animal: str):
        """
        `!fact <animal>` -> Shows a factual information about a specified animal and a picture of the animal.
        """
        if animal.lower() in ("dog","cat","panda","fox","bird","koala"):
            fact_url = f"https://some-random-api.ml/facts/{animal.lower()}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

            async with request("GET",image_url, headers=[]) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]
                else:
                    image_link = None
                     
            async with request("GET",fact_url, headers=[]) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f"{animal.title()} fact",
                                  description=data["fact"],
                                  color=ctx.author.colour)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"API returned a {response.status} status.")
        else:
            await ctx.send("No facts are avaliable for that animal.")
    
    @command(name="meme", aliases=["redditmemes"])
    async def meme(self, ctx):
        """
        `!meme` -> Shows a random meme from a random subreddit.
        """
        r = requests.get("https://memes.blademaker.tv/api")
        res = r.json()
        if (res['nsfw'] == False):
            title = res["title"]
            ups = res["ups"]
            downs = res["downs"]
            sub = res["subreddit"]
            embed = Embed(title=f"{title}\nSubreddit: {sub}")
            embed.set_image(url = res["image"])
            embed.set_footer(text=f"👍: {ups} 👎: {downs}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Not suitable content. Please try again")
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")

def setup(bot):
    bot.add_cog(Fun(bot))