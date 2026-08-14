# -*- coding: utf-8 -*-
# from PIL import Image, ImageDraw, ImageFont
from PIL import Image, ImageDraw
import psutil


class DrivesInfo:
    def __init__(self, theme):
        self.info = {}
        self.pie = {}
        self.theme = theme

        self.drive_letters = []
        for d in range(26):
            drive = f'{chr(65 + d)}:'
            self.drive_letters.append(drive)
        # self.font = ImageFont.truetype('arial.ttf', 144)

    def set_theme(self, theme):
        self.theme = theme

    def pieUsage(self, canvas=800, offs=10, hemp=100):
        for drive in self.info:
            info = self.info[drive]
            if not info:
                continue

            rate = info.used / info.total
            # DEBUG
            # import random
            # rate = random.random()

            begin = self.theme['begin']
            start = 270 + begin - 360 * rate
            end = 270 + begin

            xy = [
                (offs, hemp),
                (canvas - offs, canvas - hemp),
            ]

            img = Image.new('RGBA', (canvas, canvas))
            draw = ImageDraw.Draw(img)

            # 使用領域
            draw.pieslice(
                xy,
                start, end,
                fill=self.theme['used'],
                outline=self.theme['outline'],
                width=10,
            )
            # 空き領域
            draw.pieslice(
                xy,
                end, start,
                fill=self.theme['free'],
                outline=self.theme['outline'],
                width=10,
            )
            # draw.text((10, 10), drive, fill=self.theme['color'], font=self.font)

            if drive in self.pie:
                del self.pie[drive]
            self.pie[drive] = img

    def update(self):
        for drive in self.drive_letters:
            try:
                i = psutil.disk_usage(drive)
            except Exception:
                i = None
            self.info[drive] = i
        self.pieUsage()
