from datetime import date, datetime, timedelta
from random import choice
from discord import Embed, embeds, message
import discord
import json
from discord.ext.commands import Cog, cog
from discord.ext.commands import command, has_permissions
from ..db import db

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣",
		   "6⃣", "7⃣", "8⃣", "9⃣", "🔟")

class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polls = []

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.colours = {
                "🟥": self.bot.guild.get_role(905516061464596482), # Red
                "🟦": self.bot.guild.get_role(905515952727269429), # Blue
                "💛": self.bot.guild.get_role(918829564845772840), # Newbie
                "🎮": self.bot.guild.get_role(906212783299895306), # Games
            }
            self.reaction_message = await self.bot.get_channel(923984210308530206).fetch_message(924032730323370054)
            self.starboard_channel = self.bot.get_channel(919366806278381578)
            self.bot.cogs_ready.ready_up("reactions")
    
    # @command()
    # @has_permissions(administrator=True, manage_roles=True)
    # async def reactrole(self, ctx, emoji, role: discord.Role,*,message):
    #     embed = discord.Embed(description=message)
    #     msg = await ctx.channel.send(embed=embed)
    #     await msg.add_reaction(emoji)

    #     with open('C:/Users/MUSTAFA/Desktop/updated-discord.py-tutorial-EP-5/lib/cogs/reactrole.json') as json_file:
    #         data = json.load(json_file)

    #         new_react_role = {'role_name': role.name, 
    #         'role_id': role.id,
    #         'emoji': emoji,
    #         'message_id': msg.id}

    #         data.append(new_react_role)

    #     with open('C:/Users/MUSTAFA/Desktop/updated-discord.py-tutorial-EP-5/lib/cogs/reactrole.json', 'w') as f:
    #         json.dump(data, f, indent=4)
    


    @command(name="createpoll", aliases=["mkpoll"])
    @has_permissions(manage_guild=True)
    async def create_poll(self, ctx, seconds: int, question: str,*options):
        """
        `!createpoll|mkpoll <seconds> <question> <options>` -> You can set options and create a vote for a specified question. (Example: !mkpoll 10 "What is your favourite color?" Red Yellow Blue Green)
        """
        if len(options) > 10:
            await ctx.send("You can only supply a maximum of 10 options.")
        else:
            embed = Embed(title="Poll",
                        description=question,
                        colour=ctx.author.colour,
                        timestamp=datetime.utcnow())
            fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
                      ("Instructions","React to cast a vote!",False)]

            for name,value,inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            
            message = await ctx.send(embed=embed)

            for emoji in numbers[:len(options)]:
                await message.add_reaction(emoji)
            
            self.polls.append((message.channel.id, message.id))

            self.bot.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now()+timedelta(seconds=seconds),
									   args=[message.channel.id, message.id])
    
    async def complete_poll(self, channel_id, message_id):
        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        most_voted = max(message.reactions, key=lambda r: r.count)

        await message.channel.send(f"The results are in and option {most_voted.emoji} was the most popular with {most_voted.count-1:,} votes!")
        self.polls.remove((message.channel.id, message.id))
            

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready and payload.message_id == self.reaction_message.id:
            current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
            await payload.member.remove_roles(*current_colours, reason="Colour role reaction.")
            await payload.member.add_roles(self.colours[payload.emoji.name], reason="Colour role reaction.")
            # await self.reaction_message.remove(payload.emoji, payload.member)
        
        # it's this basically written asese for us grab the message every single reaction only cross the message if it needs to
        elif payload.message_id in (poll[1] for poll in self.polls):
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            # stop the bot removing his own reactions| gettting users or getting a list of user from reaction 
            # is an avoidable call you would normally use an async for hover because we just want a list we can flatten a list do an await
            for reaction in message.reactions:
                if (not payload.member.bot
                    and payload.member in await reaction.users().flatten()
                    and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji, payload.member)
            
            
        elif payload.emoji.name == "⭐":
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

            if not message.author.bot and payload.member.id != message.author.id:
                msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?",message.id) or (None, 0)

                embed = Embed(title="Starred message",
                              colour=message.author.colour,
							  timestamp=datetime.utcnow())
                fields = [("Author", message.author.mention, False),
						  ("Content", message.content or "See attachment", False),
						  ("Stars", stars+1, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                if len(message.attachments):
                    embed.set_image(url=message.attachments[0].url)
                
                if not stars:
                    star_message = await self.starboard_channel.send(embed=embed)
                    db.execute("""
                        INSERT INTO starboard (RootMessageID, StarMessageID) VALUES (?, ?) """,
                        message.id, star_message.id)
                else:
                    star_message = await self.starboard_channel.fetch_message(msg_id)
                    await star_message.edit(embed=embed)
                    db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?",message.id)

            else:
                    await message.remove_reaction(payload.emoji, payload.member)
        
        # elif payload.message_id == self.reaction_message.id:
        #     with open('C:/Users/MUSTAFA/Desktop/updated-discord.py-tutorial-EP-5/lib/cogs/reactrole.json') as react_file:
        #         data = json.load(react_file)
        #         for x in data:
        #             if x['emoji'] == payload.emoji.name:
        #                 role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x['role_id'])

        #                 await payload.member.add_roles(role)

    # @command()
    # async def on_raw_reaction_remove(self, payload):
    #     with open('C:/Users/MUSTAFA/Desktop/updated-discord.py-tutorial-EP-5/lib/cogs/reactrole.json') as react_file:
    #         data = json.load(react_file)
    #         for x in data:
    #             if x['emoji'] == payload.emoji.name:
    #                 role = discord.utils.get(self.bot.get_guild(
    #                     payload.guild_id).roles, id=x['role_id'])
                    
    #                 await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)
    
    @command()
    async def show_rules(self, ctx):
        embed = Embed(title="Simyaci Server Rules",
        description="""
        Welcome to the `Simyaci` Discord server!👋

        __Rules:__
        1️⃣ **Treat others with respect**
        2️⃣ **No harassment or discrimination will be tolerated**
        3️⃣ **Do not mention politics or religion**
        4️⃣ **Do not share the same thing more than once**
        5️⃣ **Self-made content must only be shared <#906056528828710992>**
        6️⃣ **Do not make excessive use of inappropriate language**
        7️⃣ **Be mindful of channel topics and only post in appropriate channels**
        8️⃣ **Do not DM other server members without their consent**

        __Tips__
        - if you have a coding question, please provide code snippets, User sites such as Github or Code Pen for large code snippets and Discord markdown for short code snippets.
        - Do your own research nefore asking questions. We are here to help, not to do your work for you.
        - We Would for you be happy if you could introduce yourself in #channel!

        __Confirmation__
        Once you have read these rules, react with one of the following emojis to access the rest of the server.
        **🎮 Gamer**| **🟦 Blue **| **🟥 Red **
        """,
        colour=ctx.author.colour)
        await ctx.send(embed=embed)


    # @Cog.listener()
	# async def on_raw_reaction_remove(self, payload):
	# 	if self.bot.ready and payload.message_id == self.reaction_message.id:
	# 		member = self.bot.guild.get_member(payload.user_id)
	# 		await member.remove_roles(self.colours[payload.emoji.name], reason="Colour role reaction.")

def setup(bot):
    bot.add_cog(Reactions(bot))


