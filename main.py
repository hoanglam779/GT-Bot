import discord
from discord.ext import commands
from discord import app_commands, Message

from paddleocr import PaddleOCR

import pygetwindow
import pyautogui
from PIL import Image
import numpy as np
import pandas as pd
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import asyncio

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

ocr = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=True, det_model_dir="en_number_mobile_v2.0_rec_infer.tar")
# img_path = 'test-image-2.jpg'

window = pygetwindow.getWindowsWithTitle("LDPlayer")[0]
left, top = window.topleft
right, bottom = window.bottomright
window_width = right - left
window_height = bottom - top

# crop_left = int(0.066 * window_width)     # 50px / 751px ~ 6.6%
# crop_top = int(0.41 * window_height)     # 220px / 464px ~ 47.4%
# crop_right = int(0.08 * window_width)    # 100px / 751px ~ 13.3% (751 - 100 = 651)
# crop_bottom = int(0.08 * window_height)  # 10px / 464px ~ 2.2% (464 - 10 = 454)
# crop_text = int(0.1731*window_width)

def healthbar_crop_ocr(window, left, top, right, bottom):
    crop_left = int(left * window_width)
    crop_top = int(top * window_height)
    crop_right = int(right * window_width)
    crop_bottom = int(bottom * window_height)

    healthbar = window.crop((crop_left, crop_top, crop_right, crop_bottom))

    healthbar = np.array(healthbar)
    height, width, _ = healthbar.shape
    result = ocr.ocr(healthbar, cls=False)
    return result[0][0][1][0]

# 1. Create prompt
# Tọa độ tương đối cho vị trí nhấp chuột, ví dụ ở giữa cửa sổ
click_x = left + int(window_width * 0.9487)   # 96.4
click_y = top + int(window_height * 0.9262)   # 50% của chiều cao cửa sổ


# system_template = "This is my data {data}:"
# prmt_template="""
# i want you to correct the spelling and calculate the percent hp boss, just return like the format below, not any more word from you, not "Here is the corrected and formatted data:"
#
# Lv.105 Founder Elphaba (305,330,795/400,000,000) 75%
# Lv.105 Goblin Chief (55,413,567/400,000,000) 12%
# Lv.105 Nine-tailed Fox Garam (93,698,474/400,000,000) 25%
# Lv.105 Snowman General Gast (250,902,339/ 400,000,000) 55%
#
# """
# prompt_template = ChatPromptTemplate.from_messages([
#     ('system', system_template),
#     ('user', prmt_template)
# ])

# 2. Create model
# model = ChatGroq(model="llama3-8b-8192", api_key='')

# 3. Create parser
# parser = StrOutputParser()

# 4. Create chain
# chain = prompt_template | model | parser

boss_df = pd.read_csv('list_of_boss.csv')
fontb = ImageFont.truetype("assets/NanumSquareOTFExtraBold.otf", 46)
health_box = [370, 200, 370+626, 200+90]
x1, y1, x2, y2 = health_box

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

        try: 
            guild = discord.Object(id=0)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to guild {guild.id}.')
        except Exception as e:
            print(f"Error syncing commands: {e}")


    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith('dit me'):
            await message.channel.send(f'Dit me {message.author}!')

    async def on_reaction_add(self, reaction, user):
        await reaction.message.channel.send('React cc')
    

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)

def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height + 35),(48,44,52))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height+35))
    return dst

def drawProgressBar(d, x, y, w, h, progress, bg="white", fg="#360a0c"):
    # draw background
    d.ellipse((x+w, y, x+h+w, y+h), fill=bg)
    d.ellipse((x, y, x+h, y+h), fill=bg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=bg)

    # draw progress bar
    w *= progress
    d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
    d.ellipse((x, y, x+h, y+h),fill=fg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)

    return d

def gen_card_from_ocr(health_st,level,idx,boss_df):

    health, total_health = health_st.split('/')
    health = int(''.join(e for e in health if e.isdigit()))
    total_health = int(''.join(e for e in total_health if e.isdigit()))

    percent = round(health/total_health*100,1)

    element = boss_df['element'][idx]
    name = boss_df['file name'][idx]

    img = Image.open('assets/'+element+'card.jpg')
    draw = ImageDraw.Draw(img)
    font_color = (255,255,255)
    if (element == 'basic') or (element == 'light'):
      font_color = (0,0,0)
    draw.text((365, 136),name,font_color, font=fontb)
    draw.text((955, 136),str(percent)+"%",font_color, font=fontb)
    draw.text((953, 59),level,font_color, font=fontb)

    fg = (46, 46, 46)
    bg = (84, 84, 84)
    font_color = (170,170,170)

    if element == 'fire':
      bg = (89, 36, 36)
      fg = (54, 10, 12)
      font_color = (194, 151, 153)
    elif element == 'light':
      bg = (176, 145, 58)
      fg = (227, 166, 0)
      font_color = (255, 253, 196)
    elif element == 'earth':
      bg = (168, 119, 56)
      fg = (140, 80, 1)
      font_color = (66, 38, 1)
    elif element == 'dark':
      bg = (102, 41, 98)
      fg = (59, 0, 55)
      font_color = (212, 138, 206)

    draw = drawProgressBar(d=draw, x= 370, y=200, w=626, h=90,
                          progress=percent/100, bg=bg, fg=fg)

    _, _, w, h = draw.textbbox((0, 0), text=health_st, font=fontb)
    w-=120
    x = (x2 - x1 - w)/2 + x1
    y = (y2 - y1 - h)/2 + y1
    draw.text((x, y), health_st,font_color, align='center', font=fontb)

    boss_sprite = Image.open('assets/bosses/'+boss_df['file name'][idx]+'.png')
    img.paste(boss_sprite,(40,-10),boss_sprite)
    return img


GUILD_ID = discord.Object(id=0)

@client.tree.command(name="hello", description="Says hello", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')

@client.tree.command(name="bosscheck", description="Kiem tra dmg boss", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):

    await interaction.response.defer()
    # Thực hiện sự kiện nhấp chuột
    pyautogui.click(click_x, click_y)
    # Đợi một chút để cửa sổ phản ứng
    time.sleep(1)
    window = pyautogui.screenshot(region=(left, top, window_width, window_height))

    panda = healthbar_crop_ocr(window, 0.066, 0.66, 0.24, 0.69)
    viper = healthbar_crop_ocr(window, 0.41, 0.43, 0.59, 0.47)
    worm = healthbar_crop_ocr(window, 0.32, 0.84, 0.51, 0.87)
    slime = healthbar_crop_ocr(window, 0.73, 0.512, 0.9, 0.55)
    level = healthbar_crop_ocr(window, 0.4, 0.47, 0.47, 0.53)

    cards=[]
    cards.append(gen_card_from_ocr(panda ,level, 0, boss_df))
    cards.append(gen_card_from_ocr(viper ,level, 1, boss_df))
    cards.append(gen_card_from_ocr(worm ,level, 3, boss_df))
    cards.append(gen_card_from_ocr(slime ,level, 2, boss_df))

    for i in range(len(cards)-1):
        cards[0] = get_concat_v(cards[0],cards[i+1])
    cards[0].save('assets/big_ass_card.jpg')
    car = discord.File('assets/big_ass_card.jpg')
    embed = discord.Embed()
    embed.set_image(url='attachment://big_ass_card.jpg')

    await interaction.followup.send(embed = embed, file= car)

client.run("")

