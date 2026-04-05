import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()


class MyBotClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="$", intents=discord.Intents.all())

    async def setup_hook(self):
        for FileName in os.listdir("./cmds"):
            if FileName.endswith(".py"):
                await bot.load_extension(f"cmds.{FileName[:-3]}")
        await self.tree.sync()


bot = MyBotClient()


@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    print(">>Bot is Online<<")


@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f"cmds.{extension}")
    await ctx.send(f"Loaded {extension}")


@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f"cmds.{extension}")
    await ctx.send(f"Reloaded {extension}")


@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f"cmds.{extension}")
    await ctx.send(f"Unloaded {extension}")


if __name__ == "__main__":
    bot.run("")
