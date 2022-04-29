import os
import re
from dataclasses import dataclass

import aqt
import aqt.browser.previewer
import aqt.deckbrowser
import aqt.editor
import aqt.theme
import aqt.webview
from aqt.utils import showWarning


# configuration keys
FOLDER_WITH_WALLPAPERS = "folder_with_wallpapers"
ENABLED_FOR = "enabled_for"
LIGHT_WALLPAPER_INDEX = "light_wallpaper_index"
DARK_WALLPAPER_INDEX = "dark_wallpaper_index"

# enabled_for tags
MAIN_WINDOW = "main_window"
ADD_CARDS = "add_cards"
EDIT_CURRENT = "edit_current"
EDIT = "edit"
PREVIEWER = "previewer"

ENABLED_FOR_TAGS = {MAIN_WINDOW, ADD_CARDS, EDIT_CURRENT, EDIT, PREVIEWER}


tag_to_dialog_class_names = {
    ADD_CARDS: "AddCards",
    EDIT_CURRENT: "EditCurrent",
    EDIT: "Edit",
}


tag_to_dialog_tag = {
    ADD_CARDS: "AddCards",
    EDIT_CURRENT: "EditCurrent",
    EDIT: "foosoft.ankiconnect.Edit",
}


########################################################################################


def check_if_data_has_key_of_type(data, key, cls, type_name):
    if key not in data:
        return f"Configuration does not have the key '{key}'"

    if not isinstance(data[key], cls):
        return f"Configuration key '{key}' must be a {type_name}"


def is_dark_mode():
    return aqt.theme.theme_manager.night_mode


########################################################################################


@dataclass
class EnabledFor:
    webview_titles: list[str]
    dialog_class_names: list[str]
    dialog_tags: list[str]
    errors: list[str]

    @classmethod
    def from_data(cls, data):
        result = cls([], [], [], [])

        if error := check_if_data_has_key_of_type(data, ENABLED_FOR, list, "list"):
            result.errors.append(error)
        elif bad_tags := ENABLED_FOR_TAGS - {*data[ENABLED_FOR]}:
            bad_tags_str = ', '.join(f"'{bad_tag}'" for bad_tag in bad_tags)
            result.errors.append(
                f"Unexpected values for configuration key '{ENABLED_FOR}':"
                f" {bad_tags_str}"
            )
        else:
            enabled_for_tags = data[ENABLED_FOR]

            if MAIN_WINDOW in enabled_for_tags:
                result.webview_titles += ["top toolbar", "main webview", "bottom toolbar"]

            if PREVIEWER in enabled_for_tags:
                result.webview_titles += ["previewer"]

            for tag in [ADD_CARDS, EDIT_CURRENT, EDIT]:
                if tag in enabled_for_tags:
                    result.dialog_class_names.append(tag_to_dialog_class_names[tag])
                    result.dialog_tags.append(tag_to_dialog_tag[tag])

        return result


########################################################################################


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

        url = file_path.replace("\\", "/")

        positions = {"center", "left", "right", "top", "bottom"} & {*file_name_parts}
        position = list(positions)[0] if positions else "center"

        dark = "dark" in file_name_parts

        return cls(url, position, dark)

Wallpaper.missing = Wallpaper("", "center", False)


@dataclass
class Wallpapers:
    light: list[Wallpaper]
    dark: list[Wallpaper]
    errors: list[str]

    @classmethod
    def from_data(cls, data):
        result = cls([], [], [])

        if error := check_if_data_has_key_of_type(data, FOLDER_WITH_WALLPAPERS, str, "string"):
            result.errors.append(error)
        else:
            folder_path = data[FOLDER_WITH_WALLPAPERS]

            try:
                file_names = os.listdir(folder_path)
            except Exception as e:
                result.errors.append(f"Error opening wallpaper folder: '{folder_path}': {e}")
            else:
                for file_name in file_names:
                    file_path = os.path.join(folder_path, file_name)

                    if '"' in file_path:
                        result.errors.append(f"File path contains quotes: '{file_path}'")

                    try:
                        with open(file_path, "r"):
                            pass
                    except Exception as e:
                        result.errors.append(f"Error opening file '{file_path}': {e}")

                    wallpaper = Wallpaper.from_file_path(file_path)

                    if wallpaper.dark:
                        result.dark.append(wallpaper)
                    else:
                        result.light.append(wallpaper)

                if not result.light:
                    result.errors.append(
                        f"Folder does not contain light wallpapers: '{folder_path}'")
                if not result.dark:
                    result.errors.append(
                        f"Folder does not contain dark wallpapers: '{folder_path}'")

        return result


########################################################################################


@dataclass
class Indexes:
    light: int
    dark: int
    errors: list[str]

    @classmethod
    def from_data(cls, data):
        result = cls(0, 0, [])

        if error := check_if_data_has_key_of_type(data, LIGHT_WALLPAPER_INDEX, int, "integer"):
            result.errors.append(error)
        else:
            result.light = data[LIGHT_WALLPAPER_INDEX]

        if error := check_if_data_has_key_of_type(data, DARK_WALLPAPER_INDEX, int, "integer"):
            result.errors.append(error)
        else:
            result.dark = data[DARK_WALLPAPER_INDEX]

        return result


########################################################################################


def show_config_errors_warning(errors):
    errors_str = '\n'.join(errors)

    showWarning(
        title="Wallpaper",
        text="Hello, this is the Wallpaper add-on! "
             "I had some issues with my configuration. "
             "Things will probably break. Sorry! "
             "(It's probably your fault, though.)"
             "\n\n"
             f"{errors_str}",
        help=None,  # noqa
    )


class Config:
    def __init__(self):
        self.enabled_for = EnabledFor([], [], [], [])
        self.wallpapers = Wallpapers([], [], [])
        self.indexes = Indexes(0, 0, [])

    def load(self):
        data = aqt.mw.addonManager.getConfig(__name__)

        self.enabled_for = EnabledFor.from_data(data)
        self.wallpapers = Wallpapers.from_data(data)
        self.indexes = Indexes.from_data(data)

        if errors := self.enabled_for.errors + self.wallpapers.errors + self.indexes.errors:
            show_config_errors_warning(errors)

    def next_wallpaper(self):
        data = aqt.mw.addonManager.getConfig(__name__)
        data[DARK_WALLPAPER_INDEX if is_dark_mode() else LIGHT_WALLPAPER_INDEX] += 1
        aqt.mw.addonManager.writeConfig(__name__, data)
        self.indexes = Indexes.from_data(data)

    @property
    def current_wallpaper(self):
        wallpapers = self.wallpapers.dark if is_dark_mode() else self.wallpapers.light
        index = self.indexes.dark if is_dark_mode() else self.indexes.light
        return wallpapers[index % len(wallpapers)] if wallpapers else Wallpaper.missing
