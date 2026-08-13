from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).with_name("title-article-creation.png")
WIDTH, HEIGHT = 1280, 720
BG = "#F5EBD7"
INK = "#333333"
ACCENT = "#E96B4C"

image = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(image)
title_font = ImageFont.truetype(r"C:\Windows\Fonts\BIZ-UDGothicB.ttc", 78)
subtitle_font = ImageFont.truetype(r"C:\Windows\Fonts\BIZ-UDGothicR.ttc", 34)

title = "記事作成の基本操作"
subtitle = "作成・入力・確認依頼の流れ"

title_box = draw.textbbox((0, 0), title, font=title_font)
title_x = (WIDTH - (title_box[2] - title_box[0])) // 2
title_y = 260
draw.text((title_x, title_y), title, font=title_font, fill=INK, stroke_width=1)

subtitle_box = draw.textbbox((0, 0), subtitle, font=subtitle_font)
subtitle_x = (WIDTH - (subtitle_box[2] - subtitle_box[0])) // 2
draw.text((subtitle_x, 390), subtitle, font=subtitle_font, fill="#555555")

underline_y = 365
draw.line((title_x, underline_y, title_x + 250, underline_y), fill=ACCENT, width=7)
draw.ellipse((title_x - 10, underline_y - 3, title_x + 3, underline_y + 10), fill=ACCENT)

image.save(OUT)
print(OUT)
