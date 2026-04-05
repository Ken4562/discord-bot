import discord
from discord.ext import commands
import json
import random
from core import Cog_Extension
from discord import app_commands


class Main(Cog_Extension):

    def __init__(self, bot):
        self.bot = bot
        self.todo = {}

    def get_user_todo_list(self, user_id: int):
        if user_id not in self.todo:
            self.todo[user_id] = {}
        return self.todo[user_id]

    @commands.command()
    async def Hello(self, ctx):
        await ctx.send("Hello, world")

    @commands.command()
    async def dice(self, ctx: commands.Context):
        await ctx.send(random.randint(1, 6))

    @app_commands.command(name="piyen", description="選一個幸運兒")
    async def piyen(self, interaction: discord.Interaction):
        members = [member for member in interaction.guild.members if not member.bot]
        if not members:
            await interaction.response.send_message("沒有可選的成員")
            return
        selected_member = random.choice(members)
        await interaction.response.send_message(
            f"今天要幹<@{selected_member.id}> 的屁眼"
        )

    @app_commands.command(name="addtodo", description="紀錄代辦事項")
    @app_commands.describe(names="名稱", importance="重要度")
    async def addtodo(
        self, interaction: discord.Interaction, names: str, importance: int
    ):
        user_id = interaction.user.id
        user_todo = self.get_user_todo_list(user_id)
        if names not in user_todo:
            user_todo[names] = importance
        else:
            await interaction.response.send_message("此代辦事項已經存在!")
        await interaction.response.send_message("新增成功!")

    @app_commands.command(name="removetodo", description="刪除代辦事項")
    @app_commands.describe(names="名稱")
    async def removetodo(self, interaction: discord.Interaction, names: str):
        user_id = interaction.user.id
        user_todo = self.get_user_todo_list(user_id)
        if names in user_todo:
            user_todo.pop(names)
            await interaction.response.send_message("刪除成功!")
        else:
            await interaction.response.send_message("此代辦事項不存在: (")

    @app_commands.command(name="cleartodo", description="清除代辦事項")
    async def cleartodo(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_todo = self.get_user_todo_list(user_id)
        if not user_todo:
            await interaction.response.send_message("沒有任何代辦事項")
        else:
            user_todo.clear()
            await interaction.response.send_message("清除成功!")

    @app_commands.command(name="sorttodo", description="依重要度排序代辦事項")
    async def sorttodo(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_todo = self.get_user_todo_list(user_id)
        if not user_todo:
            await interaction.response.send_message("沒有任何代辦事項")
        else:
            todo_sort = sorted(user_todo.items(), key=lambda x: x[1], reverse=True)
            embed = discord.Embed(title="代辦事項", color=0x738EC4)
            for name, impotance in todo_sort:
                embed.add_field(name=name, value=impotance, inline=True)
            await interaction.response.send_message(embed=embed)

    @commands.command()
    async def hh(self, ctx, msg):
        await ctx.message.delete()
        await ctx.send(msg)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await channel.send("頭香")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) == "👌":
            print("ok")
            guild = self.bot.get_guild(1335203060040859730)
            if guild is None:
                return
            role = guild.get_role(1335204866808872962)
            if role is None:
                return
            member = payload.member
            member = guild.get_member(payload.user_id)
            await member.add_roles(role)
            print(f"已為 {member.name} 添加身分組 {role.name} ")


async def setup(bot):
    await bot.add_cog(Main(bot))
