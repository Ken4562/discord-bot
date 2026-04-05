
import discord
from discord.ext import commands
import os
from core import Cog_Extension
from dotenv import load_dotenv

load_dotenv()  

class Event(Cog_Extension):

    @commands.Cog.listener()
    async def on_member_join(self, member):
        general_channel = os.getenv("general_channel")
        g_channel = self.bot.get_channel(int(general_channel))
        if g_channel is not None:
            await g_channel.send(f"歡迎<@{member.id}>加入!")

async def setup(bot):
    await bot.add_cog(Event(bot))
