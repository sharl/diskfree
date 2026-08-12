# -*- mode: python; coding: utf-8 -*-
import ctypes
import sys
import threading
import time

from PIL import Image, ImageDraw
from psutil import disk_usage
from pystray import Icon, Menu, MenuItem
import darkdetect as dd

INTERVAL = 5
PreferredAppMode = {
    'Light': 0,
    'Dark': 1,
}
# https://github.com/moses-palmer/pystray/issues/130
ctypes.windll['uxtheme.dll'][135](PreferredAppMode[dd.theme()])


class taskTray:
    def __init__(self, drive):
        self.stop_event = threading.Event()

        # 監視対象ドライブ
        self.drive = f'{drive[0]}:'.upper()

        menu = Menu(
            MenuItem(f'{self.drive} Exit', self.stopApp),
        )
        self.app = Icon(name='PYTHON.win32.diskfree', menu=menu)

    def pieDiskUsage(self, canvas=800, offs=10, hemp=100):
        while not self.stop_event.is_set():
            begin = time.time()

            disk = disk_usage(self.drive)
            rate = disk.used / disk.total

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

            self.app.title = f'{self.drive} {rate * 100:.2f}%'
            self.app.icon = img

            elapsed = time.time() - begin
            sleep_time = max(0, INTERVAL - elapsed)
            if self.stop_event.wait(sleep_time):
                break

    def stopApp(self):
        self.stop_event.set()
        self.app.stop()

    def runApp(self):
        self.stop_event.clear()

        threading.Thread(target=self.pieDiskUsage, daemon=True).start()

        self.app.run()


if __name__ == '__main__':
    drive = 'C'
    if len(sys.argv) == 2 and sys.argv[1][0].isalpha():
        drive = sys.argv[1][0]

    taskTray(drive).runApp()
