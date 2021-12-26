from discord.errors import Forbidden
from discord.ext.commands import Cog
from discord.ext.commands import command
from ..db import db


class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO exp (UserID) VALUES (?)",member.id)
        await self.bot.get_channel(905513702625804298).send(f"Welcome to **{member.guild.name}** {member.mention}! Head over to <#902993702065160247> to say hi")

        try:
            await member.send(f"Welcome to **{member.guild.name}**! Enjoy your stay!")
        except Forbidden:
            pass

        await member.add_roles(member.guild.get_role(918829564845772840))

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM exp WHERE UserID = ?",member.id)
        await self.bot.get_channel(905513702625804298).send(f"{member.display_name} has left {member.guild.name}.")


def setup(bot):
    bot.add_cog(Welcome(bot))