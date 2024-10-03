


import pygetwindow
import pyautogui
from PIL import Image
import numpy as np
import time


path = 'aaaa.jpg'
titles = pygetwindow.getAllTitles()

window = pygetwindow.getWindowsWithTitle("BlueStacks App Player")[0]
left, top = window.topleft
right, bottom = window.bottomright
window_width = right - left
window_height = bottom - top
print(left, top, right, bottom)


# Tọa độ tương đối cho vị trí nhấp chuột, ví dụ ở giữa cửa sổ
click_x = left + int(window_width * 0.9087)   # 96.4
click_y = top + int(window_height * 0.9262)   # 50% của chiều cao cửa sổ
# Thực hiện sự kiện nhấp chuột
# pyautogui.click(click_x, click_y)
# time.sleep(1)  



a = pyautogui.screenshot(region=(left, top, window_width, window_height))

crop_left = int(0.066 * window_width)     # 50px / 751px ~ 6.6%
crop_top = int(0.45 * window_height)     # 220px / 464px ~ 47.4%
crop_right = int(0.08 * window_width)    # 100px / 751px ~ 13.3% (751 - 100 = 651)
crop_bottom = int(0.08 * window_height)  # 10px / 464px ~ 2.2% (464 - 10 = 454)
crop_text = int(0.1731*window_width)
print(crop_left, crop_top, crop_right, crop_bottom)
# # Cắt ảnh với tỷ lệ thay vì giá trị cố định

a = a.crop((crop_left, crop_top, window_width - crop_right, window_height - crop_bottom))
# a = a.crop((50, 220, right - left - 100, bottom - top - 10))
a = np.array(a)
height, width, _ = a.shape
a[height-crop_text:height, width-crop_text:width] = [255, 255, 255]
# a = Image.fromarray(a)
# a.save(path)
# a.show()


from paddleocr import PaddleOCR
# Paddleocr supports Chinese, English, French, German, Korean and Japanese.
# You can set the parameter `lang` as `ch`, `en`, `french`, `german`, `korean`, `japan`
# to switch the language model in order.
ocr = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=True, det_model_dir="en_number_mobile_v2.0_rec_infer.tar") # need to run only once to download and load model into memory

text_output = ""
result = ocr.ocr(a, cls=False)
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        text_output += line[1][0] + "\n"
print(text_output)



# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq

# system_template = "This is my data {data}:"
# prmt_template="""
# i want you to correct the spelling and calculate the percent hp boss, just return like the format below, not any more word from you, not "Here is the corrected and formatted data:"

# Lv.105 Founder Elphaba (305,330,795/400,000,000) 75% 
# Lv.105 Goblin Chief (55,413,567/400,000,000) 12% 
# Lv.105 Nine-tailed Fox Garam (93,698,474/400,000,000) 25% 
# Lv.105 Snowman General Gast (250,902,339/ 400,000,000) 55%

# """
# prompt_template = ChatPromptTemplate.from_messages([
#     ('system', system_template),
#     ('user', prmt_template)
# ])

# # 2. Create model
# model = ChatGroq(model="llama3-8b-8192", api_key='')

# # 3. Create parser
# parser = StrOutputParser()

# # 4. Create chain
# chain = prompt_template | model | parser

# print(chain.invoke("""100.000.000/400,000,000 
# Ly.105 FounderFlphaba
# 20.000000/400,000,000 
# Lv.105 Goblin Chief
# 90.000.000/400,000,000 
# Ly.105 Nine-talled Fox Garam
# 100.000.000/ 400,000,000 
# Lv.105Snowman GeneralGast"""))
