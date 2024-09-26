# -*- mode: python; coding: utf-8 -*-
import sys
import time
import threading

import schedule
from pystray import Icon, Menu, MenuItem
from psutil import disk_usage
from PIL import Image, ImageDraw

INTERVAL = 60


class taskTray:
    def __init__(self, drive):
        # 監視対象ドライブ
        self.drive = f'{drive}:'.upper()

        # スレッド実行モード
        self.running = False

        menu = Menu(
            MenuItem('Exit', self.stopApp),
        )
        self.app = Icon(name='PYTHON.win32.diskfree', menu=menu)
        self.pieDiskUsage()

    def pieDiskUsage(self, canvas=800, offs=10, hemp=100):
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
        self.app.update_menu()

    def runSchedule(self):
        schedule.every(INTERVAL).seconds.do(self.pieDiskUsage)

        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stopApp(self):
        self.running = False
        self.app.stop()

    def runApp(self):
        self.running = True

        task_thread = threading.Thread(target=self.runSchedule)
        task_thread.start()

        self.app.run()


if __name__ == '__main__':
    drive = 'C'
    if len(sys.argv) == 2 and len(sys.argv[1]) == 1 and sys.argv[1].isalpha():
        drive = sys.argv[1]

    taskTray(drive).runApp()
