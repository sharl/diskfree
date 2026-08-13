# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw
import psutil


class DrivesInfo:
    def __init__(self):
        self.info = {}
        self.pie = {}

        self.drive_letters = []
        for d in range(26):
            drive = f'{chr(65 + d)}:'
            self.drive_letters.append(drive)

    def pieUsage(self, canvas=800, offs=10, hemp=100):
        for drive in self.info:
            info = self.info[drive]
            if not info:
                continue

            rate = info.used / info.total
            # DEBUG
            # import random
            # rate = random.random()

            start = 270 - 360 * rate
            end = 270

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
                fill='Blue',
                outline='Red',
                width=10,
            )
            # 空き領域
            draw.pieslice(
                xy,
                end, start,
                fill='Magenta',
                outline='Red',
                width=10,
            )
            if drive in self.pie:
                del self.pie[drive]
            self.pie[drive] = img

    def update(self):
        self.info.clear()
        for drive in self.drive_letters:
            try:
                i = psutil.disk_usage(drive)
            except Exception:
                i = None
            self.info[drive] = i
        self.pieUsage()
