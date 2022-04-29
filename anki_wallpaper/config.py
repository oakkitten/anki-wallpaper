import os
import random
import re
from dataclasses import dataclass

import aqt
import aqt.browser.previewer
import aqt.deckbrowser
import aqt.editor
import aqt.theme
import aqt.webview
from aqt.utils import showWarning

from .tools import exception_to_string


@dataclass
class Wallpaper:
    url: str
    position: str
    dark: bool

    @classmethod
    def from_file_path(cls, file_path):
        file_name = os.path.basename(file_path)
        file_name_without_extension = file_name.rsplit(".", 1)[0]
        file_name_parts = re.split(r"[-_. ]", file_name_without_extension)

        positions = {"center", "left", "right", "top", "bottom"} & {*file_name_parts}
        position = list(positions)[0] if positions else "center"

        dark_background = "dark" in file_name_parts

        return cls(file_path.replace("\\", "/"), position, dark_background)

no_wallpaper = Wallpaper("", "center", False)


def get_wallpapers_by_config_data_and_show_warning_on_error(data):
    light_wallpapers = []
    dark_wallpapers = []
    errors = []

    try:
        folder = data["folder_with_wallpapers"]
        file_names = os.listdir(folder)
        file_paths = [os.path.join(folder, file_name) for file_name in file_names]

        for file_path in file_paths:
            if '"' in file_path:
                errors.append(f"File name contains quotes: '{file_path}'")
            try:
                with open(file_path, "r"):
                    pass
            except Exception as e:
                errors.append(exception_to_string(e))
    except Exception as e:
        errors.append(exception_to_string(e))

    else:
        for file_path in file_paths:
            wallpaper = Wallpaper.from_file_path(file_path)
            (dark_wallpapers if wallpaper.dark else light_wallpapers).append(wallpaper)

        if not light_wallpapers:
            errors.append(f"Folder does not contain light wallpapers: '{folder}'")
        if not dark_wallpapers:
            errors.append(f"Folder does not contain dark wallpapers: '{folder}'")

    if errors:
        errors_str = '\n'.join(errors)
        showWarning(
            title="Wallpaper",
            text="There were issues with some of the wallpapers. "
                 "Expect things to break.\n\n"
                 f"{errors_str}\n\n"
                 "You can change settings in "
                 "Tools → Add-ons → Background image → Config.",
            help=None,  # noqa
        )

    return light_wallpapers, dark_wallpapers


class Config:
    def __init__(self):
        self.index = random.randint(1, 1000)
        self.light_wallpapers = []
        self.dark_wallpapers = []
        self.change_wallpaper_on_deck_browser = False

    def load(self):
        data = aqt.mw.addonManager.getConfig(__name__)
        self.change_wallpaper_on_deck_browser = \
            data.get("change_wallpaper_on_deck_browser", False)
        self.light_wallpapers, self.dark_wallpapers = \
            get_wallpapers_by_config_data_and_show_warning_on_error(data)

    @property
    def current_wallpaper(self):
        dark_mode = aqt.theme.theme_manager.night_mode
        wallpapers = self.dark_wallpapers if dark_mode else self.light_wallpapers
        return wallpapers[self.index % len(wallpapers)] if wallpapers else no_wallpaper

    @property
    def altered_dialogs(self):
        return ["AddCards", "EditCurrent", "Edit"]  # todo proper dialog id anki connect

