from datetime import datetime, timedelta
from typing import Awaitable, Optional
from better_profanity import profanity
from discord import Embed, Member
from discord.errors import Forbidden, HTTPException
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions
from re import search

profanity.load_censor_words_from_file('./data/profanity.txt')

class Mod(Cog):
	"""
	The Mod file contains all commands about moderation on the server. Only authorized users can use these commands.
	"""
	def __init__(self, bot):
		self.bot = bot
		self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
							# General channel | Recsources channel| Bot-commands channel
		self.links_allowed = (902993702065160247, 906056528828710992, 909389258370981888)
		self.images_allowed = (902993702065160247, 906056528828710992, 909389258370981888)


	async def kick_members(self, message, targets, reason):
		for target in targets:
			if (message.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
				await target.kick(reason=reason)

				embed = Embed(title="Member kicked",
							  colour=0xDD2222,
							  timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
						  ("Actioned by", message.author.display_name, False),
						  ("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@command(name="kick")
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def kick_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		"""
		`!kick <targets>` -> It allows one or more users on the server to be kicked out of the server.
		"""
		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:
			await self.kick_members(ctx.message, targets, reason)
			await ctx.send("Action complete.")

	# @kick_command.error
	# async def kick_command_error(self, ctx, exc):
	# 	if isinstance(exc, CheckFailure):
	# 		await ctx.send("Insufficient permissions to perform that task.")

	async def ban_members(self, message, targets, reason):
		for target in targets:
			if (message.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
				await target.ban(reason=reason)

				embed = Embed(title="Member banned",
							  colour=0xDD2222,
							  timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
						  ("Actioned by", message.author.display_name, False),
						  ("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@command(name="ban")
	@bot_has_permissions(ban_members=True)
	@has_permissions(ban_members=True)
	async def ban_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		"""
		`!ban <targets> <reason>` -> This command bans one or more people from the server without a reason if you want.
		"""
		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:
			await self.ban_members(ctx.message, targets, reason)
			await ctx.send("Action complete.")

	# @ban_command.error
	# async def ban_command_error(self, ctx, exc):
	# 	if isinstance(exc, CheckFailure):
	# 		await ctx.send("Insufficient permissions to perform that task.")


	@command(name="clear", aliases=["purge"])
	@bot_has_permissions(manage_messages=True)
	@has_permissions(manage_messages=True)
	async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 1):
		"""
		`!clear|purge <targets>` -> It allows to delete the messages of certain users with a certain limit or only deletes messages up to the specified limit.
		"""
		def _check(message):
			return not len(targets) or message.author in targets

		if 0 < limit <= 100:
			with ctx.channel.typing():
				await ctx.message.delete()
				deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow()-timedelta(days=14),
												  check=_check)

				await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)

		else:
			await ctx.send("The limit provided is not within acceptable bounds.")
            
            

	@command(name="addprofanity", aliases=["addswears","addcurses"])
	@has_permissions(manage_guild=True)
	async def add_profanity(self, ctx, *words):
		with open("./data/profanity.txt", "a", encoding="utf-8") as f:
			f.write("".join([f"{w}\n" for w in words]))

		profanity.load_censor_words_from_file("./data/profanity.txt")
		await ctx.send("Action compelete.")
	
	@command(name="delprofanity", aliases=["delswears","delcurses"])
	@has_permissions(manage_guild=True)
	async def remove_profanity(self, ctx, *words):
		with open("./data/profanity.txt", "r", encoding="utf-8") as f:
			stored = [w.strip() for w in f.readlines()]

		with open("./data/profanity.txt", "w", encoding="utf-8") as f:
			f.write("".join([f"{w}\n" for w in stored if w.strip() not in words]))

		profanity.load_censor_words_from_file("./data/profanity.txt")
		await ctx.send("Action complete.")

	@Cog.listener()
	async def on_message(self, message):
		if not message.author.bot:
			if profanity.contains_profanity(message.content):
				await message.delete()
				await message.channel.send("You can't use the word here", delete_after=10)

			elif message.channel.id not in self.links_allowed and search(self.url_regex, message.content):
				await message.delete()
				await message.channel.send("You can't send link in this channel.", delete_after=10)

			if (message.channel.id not in self.images_allowed and any([hasattr(a, "width") for a in message.attachments])):
				await message.delete()
				await message.channel.send("You can't send images here.", delete_after=10)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(909544607841415188)
			self.bot.cogs_ready.ready_up("mod")

def setup(bot):
    bot.add_cog(Mod(bot)) 