from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Bot as BotBase
from discord import Embed
from discord import Intents, DMChannel
from discord.errors import Forbidden
from discord.ext.commands.context import Context
from discord.ext.commands import Context
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown, MissingPermissions
from glob import glob
from datetime import datetime
from ..db import db
from dismusic.errors import NotConnectedToVoice, PlayerNotConnected

PREFIX = "!"
OWNER_IDS = [296339024849928192]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

# def get_prefix(bot, message):
# 	prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?",message.guild.id)
# 	return when_mentioned_or(prefix)(bot, message)

class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f" {cog} cog ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
	def __init__(self):
		self.PREFIX = PREFIX
		self.ready = False
		self.cogs_ready = Ready()
		self.guild = None
		self.scheduler = AsyncIOScheduler()

		db.autosave(self.scheduler)
		super().__init__(
			command_prefix=PREFIX, 
			owner_ids=OWNER_IDS,
			intents =Intents.all()
			)
	
	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print(f"{cog} cog loaded")

		print("setup complete ")

	def update_db(self):
		db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
					 ((guild.id,) for guild in self.guilds))

		db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
					 ((member.id,) for member in self.guild.members if not member.bot))

		to_remove = []
		stored_members = db.column("SELECT UserID FROM exp")

		for id_ in stored_members:
			print(self.guild.get_member(id_))
			if not self.guild.get_member(id_):
				to_remove.append(id_)

		db.multiexec("DELETE FROM exp WHERE UserID = ?",
						((id_,) for id_ in to_remove))
		
		db.commit()

	def run(self, version):
		self.VERSION = version

		print("running setup...")
		self.setup()

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
			self.TOKEN = tf.read()

		print("running bot...")
		super().run(self.TOKEN, reconnect=True)
	# you didn't want your bot to accept commands until the it was ready because then do if so command is not none so if command can actually be found and ctx.guild is not None this will essentially just mean that commands can't be used in DMs
	async def process_commands(self, message):
		ctx = await self.get_context(message, cls=Context)

		if ctx.command is not None and ctx.guild is not None:
			if self.ready:
				await self.invoke(ctx)

			else:
				await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

	async def rules_reminder(self):
		await self.stdout.send("""
		**1. Be respectful**
		You must respect all users, regardless of your liking towards them. Treat others the way you want to be treated.

		**2. No Inappropriate Language**
		The use of profanity should be kept to a minimum. However, any derogatory language towards any user is prohibited.

		**3. No spamming**
		Don't send a lot of small messages right after each other. Do not disrupt chat by spamming.

		**4. No pornographic/adult/other NSFW material**
		This is a community server and not meant to share this kind of material.

		**5. No advertisements**
		We do not tolerate any kind of advertisements, whether it be for other communities or streams. You can post your content in the media channel if it is relevant and provides actual value (Video/Art)

		**6. No offensive names and profile pictures**
		You will be asked to change your name or picture if the staff deems them inappropriate.

		**7. Server Raiding**
		Raiding or mentions of raiding are not allowed.

		**8. Direct & Indirect Threats**
		Threats to other users of DDoS, Death, DoX, abuse, and other malicious threats are absolutely prohibited and disallowed.

		**9. Follow the Discord Community Guidelines**
		You can find them here: https://discordapp.com/guidelines

		**10. Do not join voice chat channels without permission of the people already in there**
		If you see that they have a free spot it is alright to join and ask whether they have an open spot, but leave if your presence is not wanted by whoever was there first.

		**The Admins and Mods will Mute/Kick/Ban per discretion. If you feel mistreated dm an Admin and we will resolve the issue.**

		All Channels will have pinned messages explaining what they are there for and how everything works. If you don't understand something, feel free to ask!

		**Your presence in this server implies accepting these rules, including all further changes. These changes might be done at any time without notice, it is your responsibility to check for them.**
		""")


	async def on_connect(self):
		
		print("bot connected")

	async def on_disconnect(self):
		print("bot disconnected")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Something went wrong.")

		await self.stdout.send("An error occured.")
		raise

	async def on_command_error(self, ctx, exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send("One or more required arguments are missing.")

		elif isinstance(exc, CommandOnCooldown):
			await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.")
		
		elif isinstance(exc, MissingPermissions):
			await ctx.send("Insufficient permissions to perform that task.")
		
		elif isinstance(exc, PlayerNotConnected):
			await ctx.send("Player is not connected to any voice channel.")

		elif isinstance(exc, NotConnectedToVoice):
			await ctx.send(f"You are not connected to any voice channel.")

		elif hasattr(exc, "original"):
			# if isinstance(exc.original, HTTPException):
			# 	await ctx.send("Unable to send message.")

			if isinstance(exc.original, Forbidden):
				await ctx.send("I do not have permission to do that.")

			else:
				raise exc.original

		else:
			raise exc


	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(902993702065160244)
			self.stdout = self.get_channel(902993702065160247)
			self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
			self.scheduler.start()
			
			self.update_db()

			await self.stdout.send("Now online!")

			self.ready = True
			print("bot ready")

		else:
			print("bot reconnected")

	# For DM messages to bot
	# Mod mail system
	async def on_message(self, message):
		if not message.author.bot:
			if isinstance(message.channel, DMChannel):
				if len(message.content) < 50:
					await message.channel.send("Your message should be at least 50 characters")
				else:
					member = self.guild.get_member(message.author.id)
					embed = Embed(title="Modmail",
							  colour=message.author.color,
							  timestamp=datetime.utcnow())

					embed.set_thumbnail(url=member.avatar_url)

					fields = [("Member", message.author.display_name, False),
							  ("Message", message.content, False)]
					
					for name,value,inline in fields:
						embed.add_field(name=name, value=value, inline=inline)
					mod = self.get_cog('Mod')
					await mod.log_channel.send(embed=embed)
					await message.channel.send("Message relayed to moderator.")
			else:
				await self.process_commands(message)
			


bot = Bot()