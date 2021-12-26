from datetime import datetime
from typing import Optional
from discord import Embed, Member
from discord.ext.commands import Cog, BadArgument
from discord.ext.commands import command
import googletrans
import discord




class Info(Cog):
    """
    The Info file contains all commands for getting information about users in the server, server itself and roles. Extra commands can be add for helping user.
    """
    def __init__(self, bot):
        self.bot = bot
        

    @command(name="userinfo", aliases=["memberinfo","ui"])
    async def user_info(self, ctx, target: Optional[Member]):
        """
        `!userinfo|memberinfo|ui <target>` -> Shows information about target user or itself.
        """
        target = target or ctx.author

        embed = Embed(
            title="User Information",
            colour=target.colour,
            timestamp=datetime.utcnow()) 
        
        embed.set_thumbnail(url=target.avatar_url)

        fields = [("Name", str(target), True),
                  ("ID",target.id, False),
                  ("Bot?", target.bot, True),
                  ("Top role", target.top_role.mention, True),
                  ("Status", str(target.status).title(), True),
				  ("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
                  ("Created at", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                  ("Joined at,", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                  ("Boosted", bool(target.premium_since), True)]

        for name,value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @command(name="serverinfo", aliases=["guildinfo","si","gi"])
    async def server_info(self, ctx):
        """
        `!serverinfo|si` -> Shows information about server.
        """
        embed = Embed(title="Server information",
                        colour=discord.Color.dark_blue(),
					  timestamp=datetime.utcnow())
        
        embed.set_thumbnail(url=ctx.guild.icon_url)

        guild = ctx.guild
        roles = [role for role in guild.roles if role != ctx.guild.default_role]

        fields = [("ID", ctx.guild.id, True),
                ("Owner", ctx.guild.owner, True),
                ("Region", ctx.guild.region, True),
                ("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                ("Members", len(ctx.guild.members), True),
                ("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
                ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
                ("Banned members", len(await ctx.guild.bans()), True),
                ("Text channels", len(ctx.guild.text_channels), True),
                ("Voice channels", len(ctx.guild.voice_channels), True),
                ("Categories", len(ctx.guild.categories), True),
                ("Invites", len(await ctx.guild.invites()), True),
                ("Server Roles", f" ".join([role.mention for role in roles]), False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(pass_context=True)
    async def roles(self, ctx):
        """
        `!roles` -> Shows the roles on the server.
        """
        guild = ctx.guild
        roles = [role for role in guild.roles if role != ctx.guild.default_role]
        embed = discord.Embed(title="Server Roles", description=f" ".join([role.mention for role in roles]))
        await ctx.send(embed=embed)
        

    # @commands.command()
    # async def shutdown(self,ctx):
    #     if ctx.message.author.id == 902994730059714560: #replace OWNERID with your user id
    #         print("shutdown")
    #     try:
    #         await self.bot.logout()
    #     except:
    #         print("EnvironmentError")
    #         self.bot.clear()
    #     else:
    #         await ctx.send("You do not own this bot!")
    

    @command(aliases=["trans","tr"])
    async def translate(self, ctx, lang_to, *args):
        """
        `!translate|trans|tr <lang_to> <text>` -> You can translate texts with using this command. Example usage: !translate tr Hello World. [click to see language shortcuts](https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages)
        """
        lang_to = lang_to.lower()
        if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
            raise BadArgument("Invalid language to translate text to")
        
        text = ' '.join(args)
        translator = googletrans.Translator()
        text_translated = translator.translate(text, dest=lang_to).text
        await ctx.send(text_translated)

    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("info")
    
def setup(bot):
    bot.add_cog(Info(bot))