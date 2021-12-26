import discord
from discord.ext.commands import Cog

intents = discord.Intents.default()
intents.members = True



class Music(Cog):
    """
    The music file contains all the commands that you can listen to music in audio channels and help you.
    """
    def __init__(self, bot):
        self.bot = bot
        self.bot.lava_nodes = [
    {
        'host':'lava.link',
        'port':80,
        'rest_uri': 'http://lava.link:80',
        'identifier':'anything',
        'password':'anything',
        'region':'singapore'
    }
]

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.load_extension('dismusic')
            self.bot.load_extension('dch')
            self.bot.cogs_ready.ready_up("music")
    
    
    

def setup(bot):
    bot.add_cog(Music(bot))