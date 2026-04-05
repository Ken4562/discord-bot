import discord
from discord.ext import commands
from discord import app_commands
import json 
from core import Cog_Extension
import random

with open('validword.json', 'r') as validword_json_file:  # 所有可猜單字
    validword_list = json.load(validword_json_file)

with open('wordle.json', 'r') as wordle_json_file:  # wordle答案庫
    wordle_list = json.load(wordle_json_file)

class Wordle(Cog_Extension):     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_attempts = 6
        self.attempts_times = 0
        self.answer_word = ""
        self.not_in_answer_letters = ""

    @app_commands.command(name = "wordle", description = "play wordle")
    @app_commands.describe()
    async def wordle(self, interaction: discord.Interaction):
        self.answer_word = random.choice(wordle_list)   # 選字
        print(self.answer_word)
        self.attempts_times = 0
        self.not_in_answer_letters = ""
        await interaction.response.send_message("你有6次機會猜一個長度為5的單字\n使用指令 /guess (單字)")    
    
    @app_commands.command(name = "guess", description = "guess word")
    @app_commands.describe(word = "word")
    async def guess(self, interaction: discord.Interaction, word: str):

        if len(word) != 5:
            await interaction.response.send_message("請輸入5個字母")
            return        
        if not word.isalpha():
            await interaction.response.send_message("請輸入有效的字母！")
            return        
        if word not in validword_list:
            await interaction.response.send_message(f"{word}不是個單字") 
            return
        if not self.answer_word:
            await interaction.response.send_message("請先使用 /wordle 開始遊戲")
            return
                
        display_word = "" 
        if word == self.answer_word:  
            await interaction.response.send_message(f"恭喜你猜中了！單詞是：{self.answer_word}")
            return
        
        self.attempts_times += 1  # 機會減1
        answer_letter_counts = {letter: self.answer_word.count(letter) for letter in set(self.answer_word)}
        # 計算每個字母在答案中的出現次數

        for i in range(5):
            if word[i] in self.answer_word and answer_letter_counts[word[i]] > 0:  # 有出現且前面沒出現過
                if word[i] == self.answer_word[i]:  # 位置對
                    display_word += ":green_square:"
                else:
                    display_word += ":yellow_square:"  # 位置錯
                answer_letter_counts[word[i]] -= 1  # 避免重複
            elif word[i] not in self.not_in_answer_letters and word[i] not in self.answer_word:  # 沒出現且沒被加進not in answer list
                self.not_in_answer_letters += word[i]
                display_word += ":black_large_square:"
            else:   #沒出現且已被加進not in answer list
                display_word += ":black_large_square:"

        display_word += f"\n{word}  已排除的單字: {",".join(self.not_in_answer_letters)}\n剩下{6 - self.attempts_times}次機會"

        if self.attempts_times >= self.max_attempts:
            await interaction.response.send_message(f"遊戲結束！你沒有猜中單詞。正確答案是：{self.answer_word}")
            return
        
        print(display_word)
        await interaction.response.send_message(display_word)

async def setup(bot):
    await bot.add_cog(Wordle(bot))
