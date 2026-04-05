import discord
from discord.ext import commands
from discord.ext import tasks
import os
from core import Cog_Extension

class Task(Cog_Extension):

    '''
TODO (optional)
    Add tasks that would loop in background
    Reference : 
    https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html?highlight=loop#discord.ext.tasks.loop 
    '''

    def __init__(self,*args):
        super().__init__(*args)

async def setup(bot):
    await bot.add_cog(Task(bot))