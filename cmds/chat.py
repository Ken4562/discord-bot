import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
from google import genai
from google.genai import types
import requests
from PIL import Image
import re


# 確保文件夾存在
if not os.path.exists("./chat_ai_img"):
    os.makedirs("./chat_ai_img")

load_dotenv()
client = genai.Client(api_key=os.getenv("gemini_api_key1"))
SYSTEM_BEHAVIOR = "[請模仿日本歌手Aimer(エメ)的言行舉止回覆，可以回答中適當的插入顏文字，請盡可能的回答問題但不要影響到資訊的正確性。注:1.回答語言請以繁體中文為主。]"
SAFETY_SETTINGS = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_NONE,
    ),
]


def sanitize_filename(url: str) -> str:
    # 去掉 URL 中的 query 參數，並過濾無效字符
    filename = re.sub(r"[^\w\-_\. ]", "_", url.split("/")[-1].split("?")[0])
    return filename


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="chat", help="和機器人聊天")
    async def chat(self, ctx: commands.Context, question: str, image_url: str = None):
        if not question:
            await ctx.send(
                embed=Embed(
                    description=f"請輸入要詢問的內容", color=discord.Color.yellow()
                )
            )
            return
        elif len(question) >= 2000:
            await ctx.send(
                embed=Embed(
                    description=f"請求發生錯誤: 輸入字數過多，長度必須為 2000 或更少。",
                    color=discord.Color.red(),
                )
            )
            return
        else:
            try:
                embed = discord.Embed(
                    title="使用者提問:",
                    description=f"{question}",
                    color=discord.Color.green(),
                )
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)

                image_path = None
            except Exception as e:
                await ctx.send(
                    embed=Embed(
                        description=f"請求發生錯誤: {e}", color=discord.Color.red()
                    )
                )
            try:
                if image_url:
                    # 下載圖片並存儲
                    sanitized_filename = sanitize_filename(image_url)
                    image_path = f"./chat_ai_img/{sanitized_filename}"
                    response = requests.get(image_url)
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    img = Image.open(image_path)

                    # 使用 Gemini 模型生成描述
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[question, img],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_BEHAVIOR,
                            safety_settings=SAFETY_SETTINGS,
                        ),
                    )
                else:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[question],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_BEHAVIOR,
                            safety_settings=SAFETY_SETTINGS,
                        ),
                    )

                if response and hasattr(response, "text"):
                    response_text = response.text
                    for chunk in [
                        response_text[i : i + 1900]
                        for i in range(0, len(response_text), 1900)
                    ]:
                        await ctx.send(embed=Embed(description=chunk, color=0x39C5BB))

            except Exception as e:
                await ctx.send(
                    embed=Embed(
                        description=f"請求發生錯誤: {e}", color=discord.Color.red()
                    )
                )
            finally:
                # 刪除本次詢問的圖片
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)

    @app_commands.command(name="chat", description="和機器人聊天")
    @app_commands.describe(question="訊息內容", image_url="圖片網址")
    async def chat_app(
        self, interaction: discord.Interaction, question: str, image_url: str = None
    ):
        await interaction.response.defer()
        if not question:
            await interaction.response.send_message(
                embed=Embed(
                    description=f"請輸入要詢問的內容", color=discord.Color.yellow()
                ),
                ephemeral=True,
            )
            return
        elif len(question) >= 2000:
            await interaction.response.send_message(
                embed=Embed(
                    description=f"請求發生錯誤: 輸入字數過多，長度必須為 2000 或更少。",
                    color=discord.Color.red(),
                )
            )
            return
        else:
            try:
                embed = discord.Embed(
                    title="使用者提問:",
                    description=f"{question}",
                    color=discord.Color.green(),
                )
                embed.set_image(url=image_url)
                await interaction.followup.send(embed=embed)

                image_path = None
            except Exception as e:
                await interaction.followup.send(
                    embed=Embed(
                        description=f"請求發生錯誤: {e}", color=discord.Color.red()
                    )
                )
            try:
                if image_url:
                    # 下載圖片並存儲
                    sanitized_filename = sanitize_filename(image_url)
                    image_path = f"./chat_ai_img/{sanitized_filename}"
                    response = requests.get(image_url)
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    img = Image.open(image_path)

                    # 使用 Gemini 模型生成描述
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[question, img],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_BEHAVIOR,
                            safety_settings=SAFETY_SETTINGS,
                        ),
                    )
                else:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[question],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_BEHAVIOR,
                            safety_settings=SAFETY_SETTINGS,
                        ),
                    )

                if response and hasattr(response, "text"):
                    response_text = response.text
                    for chunk in [
                        response_text[i : i + 1900]
                        for i in range(0, len(response_text), 1900)
                    ]:
                        await interaction.followup.send(
                            embed=Embed(description=chunk, color=0x39C5BB)
                        )

            except Exception as e:
                await interaction.followup.send(
                    embed=Embed(
                        description=f"請求發生錯誤: {e}", color=discord.Color.red()
                    )
                )
            finally:
                # 刪除本次詢問的圖片
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)


async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
