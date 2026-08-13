# -*- coding: utf-8 -*-
import ctypes
import threading
import time

from PIL import Image
from pystray import Icon, Menu, MenuItem
import darkdetect as dd

from DrivesInfo import DrivesInfo
from utils import resource_path


TITLE = 'diskfree'
INTERVAL = 5
PreferredAppMode = {
    'Light': 0,
    'Dark': 1,
}
# https://github.com/moses-palmer/pystray/issues/130
ctypes.windll['uxtheme.dll'][135](PreferredAppMode[dd.theme()])
THEMES = {
    'Default': {
        'color': 'White',
        'used': 'Blue',
        'free': 'Magenta',
        'outline': 'Red',
        'begin': 0,
    },
    'Pacman': {
        'color': 'Yellow',
        'used': 'Yellow',
        'free': 'Black',
        'outline': None,
        'begin': 180 + 45,
    },
}


class Drive:
    def __init__(self, drive):
        self.drive = drive

        image = Image.open(resource_path('Assets/sample.ico'))
        # main_menu = Menu(
        #     MenuItem('Exit', self.stopApp),
        # )
        # self.app = Icon(name=self.drive, title=self.drive, icon=image, menu=main_menu)
        self.app = Icon(name=self.drive, title=self.drive, icon=image)
        # print('init', self.drive)

    def update(self, title, image):
        self.app.title = title
        self.app.icon = image

    def stopApp(self):
        self.app.stop()
        # print('stop', self.drive)


class DiskFree:
    def __init__(self):
        self.stop_event = threading.Event()

        self.theme = list(THEMES)[0]
        self.drives = DrivesInfo(THEMES[self.theme])

        # update enables
        self.drives.update()
        self.enable_drives = {
            drive: self.drives.info[drive] is not None for drive in self.drives.drive_letters
        }
        self.drive_threads = {}

        image = Image.open(resource_path('Assets/sample.ico'))
        theme_menu = []
        for theme in THEMES:
            theme_menu.append(
                MenuItem(theme, self.set_theme, checked=lambda x: str(x) == self.theme),
            )
        enable_menu = []
        for drive in self.enable_drives:
            enable_menu.append(
                MenuItem(drive, self.toggle_enables, checked=lambda item: self.enable_drives[str(item)])
            )
        main_menu = Menu(
            MenuItem('Theme', Menu(*theme_menu)),
            Menu.SEPARATOR,
            MenuItem('Monitor Drives', Menu(*enable_menu)),
            Menu.SEPARATOR,
            MenuItem('Exit', self.stopApp),
        )
        self.app = Icon(name=TITLE, title=TITLE, icon=image, menu=main_menu)

    def set_theme(self, _, item):
        self.theme = str(item)
        self.drives.set_theme(THEMES[self.theme])

    def toggle_enables(self, _, item):
        drive = str(item)
        if self.drives.info[drive]:
            self.enable_drives[drive] = not self.enable_drives[drive]
        # print(f'set {drive} to {self.enable_drives[drive]}')

    def monitor(self):
        while not self.stop_event.is_set():
            begin = time.time()

            self.drives.update()

            for drive in self.drives.info:
                i = self.drives.info[drive]
                if i:
                    if self.enable_drives[drive]:
                        title = f'{drive} {i.used / i.total:.2%}'
                        image = self.drives.pie[drive]
                        if drive not in self.drive_threads:
                            self.drive_threads[drive] = Drive(drive)
                            threading.Thread(name=drive, target=self.drive_threads[drive].app.run, daemon=True).start()
                        self.drive_threads[drive].update(title, image)
                    else:
                        if drive in self.drive_threads:
                            self.drive_threads[drive].stopApp()
                            # print('disable', drive)

            # clean up
            thread_names = [th.name for th in threading.enumerate()]
            for drive in self.drive_threads.copy():
                if drive not in thread_names:
                    del self.drive_threads[drive]

            # print('dirve_threads', self.drive_threads)

            elapsed = time.time() - begin
            sleep_time = max(0, INTERVAL - elapsed)
            if self.stop_event.wait(sleep_time):
                break

    def stopApp(self):
        self.stop_event.set()

        for drive in self.drive_threads:
            self.drive_threads[drive].stopApp()

        self.app.stop()

    def runApp(self):
        self.stop_event.clear()
        threading.Thread(name='monitor', target=self.monitor, daemon=True).start()
        self.app.run()


ICON = """
89504e470d0a1a0a0000000d4948445200000010000000100803000000282d0f530000000467414d410000b18f0bfc6105000000206348524d00007a
26000080840000fa00000080e8000075300000ea6000003a98000017709cba513c000001d7504c54450000000101010f0d0b00010103080a00020300
00000000000000001334451131410000000000001f54701b4b630000001e536f1b4a63000000081820256486225d7b08161d0000000000000b1e2824
6384235f7f08182000000000000000000008141a1c4b63276b8e2565871c4c650611160000000000002625238c8d89215b7907151d0000000000000f
212b979a970a1d260000000000002156721c4c66000000000000215a791d506b000000215b790000001f55711b4c650000000000000a1d2625668723
6080091a23000000010304050f14091c26235e7e236080091a23050f140001010001020002030002030002030001020102033ba1d63b9fd43ca3d83e
a7de3ba0d598c6da48ade13ca6de3da6de3da6dd3ea9e1399ccfd9e5e476c0e447abdf50b0e13ca6dd43a9df3da7df3a9fd392c8e16fbce345aadf7d
b6d192b2bf5ab3e05db4df93b2bf77b6d43ba1d741aae15bb6e4a4acab6f67619fd0e5a4d1e36e655faab7b854b3e33ea8e03eaae2439fd37d6d8b94
a8b891a9b067b9e26bbbe191a8b093a6b87c698842a0d53ba3d9479ed29b2f409a4a5c6f9ec34c91c24d91c2729bbf9c405099314145a0d43286b257
81ab983649933a4e933c5094394d96394d5384b03185b12d61812f5e7dffffffd3f96a210000005374524e530000000000001e1a199c93154ffaf645
fbf80669fcf95f043e73e8e36c37030259e4fdfed84e01076ae5e15f050c77ed640962efe95270fdfa5efd61eee7510b74ece761080762a2eee59d59
0b6f8786886305f4f0d3c000000001624b47449c71bcc2270000000774494d4507e8090e08280661217c2a000000d74944415418d363608000367606
14c0c1c9c58d22c0c3cbc78f2a2020882220242c222a268ee04a484a058748cbc8ca81b98cf20a8a4aa16161e1ca2aaa6a8c0c0c4cea1a9a119151d1
3151b1715ada3acc0cba7afaf1098949c9c94929a9695206860c46c6e9199959d939b979f929a90526a60c66e685c945c525a565e51595c95516960c
6656d535b575f50d8d4dcd2dadb140016b9bb6f68eceaeee9edebefe09c1b6760cf60e8e13274d9e3275eab4e933663a39bb30b0b8bab97bcc9a0d04
b33cbdbcc599812e63f6f1f5f3078280c0205606060074d237e8377bca260000002574455874646174653a63726561746500323032342d30392d3133
5432333a34303a30362b30393a3030d2b5b6cf0000002574455874646174653a6d6f6469667900323032342d30392d31335432333a34303a30362b30
393a3030a3e80e730000000049454e44ae426082
"""

if __name__ == '__main__':
    DiskFree().runApp()
