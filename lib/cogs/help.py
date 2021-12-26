from datetime import datetime
from typing import Optional
import discord
from discord import Embed, Member
from discord.colour import Colour
from discord.ext.commands import Cog, MinimalHelpCommand
from discord.ext.commands import command


class Help(Cog):
    """
    This Help cog contains all commands explanation and usage. Type hp|fullhelp or helpcommands to see a list of all commands.
    """
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")
    
    @command(name="helpcommands", aliases=["hp","fullhelp"])
    async def show_help(self, ctx):
        embed = Embed(title=f"Help Command",
                    description="Shows information about server commands.",
                    colour=ctx.author.colour,
                    timestamp=datetime.utcnow())
        
        fields = [("Server Info","`!serverinfo|si` -> Shows information about server.",False),
                  ("User Info","`!userinfo|memberinfo|ui <target>` -> Shows information about target user or itself.",False),
                  ("Roles","`!roles` -> Shows the roles on the server.",False),
                  ("Kicking Users","`!kick <targets>` -> It allows one or more users on the server to be kicked out of the server.",False),
                  ("Banning Users","`!ban <targets> <reason>` -> This command bans one or more people from the server without a reason if you want.",False),
                  ("Rank","`!rank <target>` -> Shows the level ranking of the specified person on the server.",False),
                  ("Level","`!level <target>` -> Shows the level and xp status of the specified person on the server.",False),
                  ("Leaderboard On the Server","`!leaderboard` -> Show the status of level, rank and xp for each user on the server.",False),
                  ("Make a poll","`!createpoll|mkpoll <seconds> <question> <options>` -> You can set options and create a vote for a specified question. (Example: !mkpoll 10 'Your favourite color?' Red Yellow Blue Green)",False),
                  ("Translator","`!translate|trans|tr <lang_to> <text>` -> You can translate texts with using this command. Example usage: !translate tr Hello World ",False),
                  ("Deleting Messages","`!clear|purge <targets>` -> It allows to delete the messages of certain users with a certain limit or only deletes messages up to the specified limit.",False),
                  ("Toss a coin","`!coin` -> Toss a coin and see if it comes up heads or tails.",False),
                  ("Dice Roller","`dice|roll <roll_number>d<dice_side_number>` -> This command creates a dice with as many faces as you want and you can choose how many times you can roll, and prints the sum of the dices rolled.",False),
                  ("Animal Fact","`!fact <animal>` -> Shows a factual information about a specified animal and a picture of the animal.",False),
                  ("Random meme","`!meme` -> Shows a random meme from a random subreddit.",False),
                  ("Echo Message","`echo|say <message>` -> bot writes the same message as you typed.",False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)
    

    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("help")
def setup(bot):
    bot.add_cog(Help(bot))