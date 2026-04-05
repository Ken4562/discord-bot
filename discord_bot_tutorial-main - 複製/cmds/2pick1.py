import discord
from discord.ext import commands
from discord import app_commands
from pytube import Playlist, YouTube
import json
import random
import asyncio


class pick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.win = ""

    @app_commands.command(name="add", description="將單曲或播放清單(公開)加入")
    @app_commands.describe(song_url="單曲或播放清單連結(公開)")
    async def add(self, interaction: discord.Interaction, song_url: str):
        await interaction.response.defer()  # 延遲回應

        try:
            song = YouTube(song_url)
            new_song_data = [{"title": song.title, "url": song.watch_url}]

        except:
            playlist = Playlist(song_url)
            new_song_data = [
                {"title": video.title, "url": video.watch_url}
                for video in playlist.videos
            ]

        with open("song.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        original_len = len(existing_data)

        for song in new_song_data:
            if song not in existing_data:
                existing_data.append(song)
        new_song_count = len(existing_data) - original_len

        with open("song.json", "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

        response = f"成功新增{new_song_count}歌曲\n共有 {len(existing_data)} 首歌曲\n\n"
        await interaction.followup.send(response)

    @app_commands.command(name="delete", description="將歌曲或播放清單(公開)刪除")
    @app_commands.describe(song_url="歌曲或播放清單連結(公開)")
    async def delete(self, interaction: discord.Interaction, song_url: str):
        await interaction.response.defer()  # 延遲回應

        try:
            song = YouTube(song_url)
            delete_song_data = [{"title": song.title, "url": song.watch_url}]

        except:
            playlist = Playlist(song_url)
            delete_song_data = [
                {"title": video.title, "url": video.watch_url}
                for video in playlist.videos
            ]

        with open("song.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)

        oringinal_len = len(existing_data)
        existing_data = [song for song in existing_data if song not in delete_song_data]

        with open("song.json", "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

        if len(existing_data) < oringinal_len:
            await interaction.followup.send(
                f"成功移除{oringinal_len - len(existing_data)}首歌曲"
            )
        else:
            await interaction.followup.send("歌曲都不在歌曲庫內")

    @app_commands.command(name="deleteall", description="將全部歌曲刪除")
    @app_commands.describe()
    async def deleteall(self, interaction: discord.Interaction):
        await interaction.response.defer()  # 延遲回應

        with open("song.json", "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

        await interaction.followup.send("成功清空歌曲庫")

    @app_commands.command(name="showsonglist", description="顯示歌曲庫")
    @app_commands.describe()
    async def showsonglist(self, interaction: discord.Interaction):

        await interaction.response.defer()

        with open("song.json", "r", encoding="utf-8") as f:
            song_list = json.load(f)

        if song_list == []:
            await interaction.followup.send("歌曲庫是空的")
            return

        songs_per_page = 24
        pages = [
            song_list[i : i + songs_per_page]
            for i in range(0, len(song_list), songs_per_page)
        ]

        for index, page in enumerate(pages):
            formatted_list = "\n".join(
                [
                    f"{index * songs_per_page + i + 1}. {song["title"]} ({song["url"]})"
                    for i, song in enumerate(page)
                ]
            )
            await interaction.followup.send(formatted_list)

    @app_commands.command(name="2pick1", description="二選一")
    @app_commands.describe(number="幾強")
    async def pick(self, interaction: discord.Interaction, number: int):
        await interaction.response.defer()
        m = number & number - 1
        if m == 0:
            round = number
            with open("song.json", "r", encoding="utf-8") as f:
                self.alllink = []
                self.alllink = [song["url"] for song in json.load(f)]
                self.links = random.sample(self.alllink, number)
            random.shuffle(self.links)
            while len(self.links) > 1:
                next_round = []
                for i in range(0, len(self.links), 2):
                    video1 = self.links[i]
                    video2 = self.links[i + 1]
                    await self.send(interaction, video1, video2)
                    next_round.append(self.win)
                round //= 2
                self.links = next_round
                await interaction.channel.send(f"進入{round}強")

            await interaction.channel.send("冠軍歌曲是：" + self.links[0])
        else:
            await interaction.followup.send(content="請輸入2的次方!")

    def get_video_details(self, url):
        video = YouTube(url)
        return {
            "title": video.title,
            "url": video.watch_url,
        }

    async def send(self, interaction: discord.Interaction, video1, video2):
        self.win = ""

        async def button1_callback(interaction: discord.Interaction):
            self.win = video1
            await interaction.response.send_message(content="你選擇了第一首歌!")
            view.stop()

        async def button2_callback(interaction: discord.Interaction):
            self.win = video2
            await interaction.response.send_message(content="你選擇了第二首歌!")
            view.stop()

        view = discord.ui.View(timeout=None)
        button1 = discord.ui.Button(
            label="選擇第一首歌!", style=discord.ButtonStyle.blurple
        )
        button2 = discord.ui.Button(
            label="選擇第二首歌!", style=discord.ButtonStyle.blurple
        )

        button1.callback = button1_callback
        button2.callback = button2_callback

        view.add_item(button1)
        view.add_item(button2)

        video1_details = self.get_video_details(video1)
        video2_details = self.get_video_details(video2)

        message = await interaction.channel.send(
            content=f"歌曲1\n{video1_details['url']}\n歌曲2\n{video2_details['url']}",
            view=view,
        )

        await message.edit(content=message.content)

        await view.wait()


async def setup(bot):
    await bot.add_cog(pick(bot))
