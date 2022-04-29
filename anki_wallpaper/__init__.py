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
from aqt import gui_hooks
from aqt.qt import Qt, QColor
from aqt.utils import showWarning

from .anki_tools import get_dialog_instance_or_none
from .tools import append_to_method, replace_method, exception_to_string


anki_version = tuple(int(segment) for segment in aqt.appVersion.split("."))


def set_main_window_wallpaper():
    aqt.mw.setStyleSheet(rf"""
        QMainWindow {{
            background-image: url("{config.current_wallpaper.url}"); 
            background-position: {config.current_wallpaper.position};
        }}
        
        QMenuBar {{ background: transparent; }}
        #centralwidget {{  background: transparent; }}
    """)


def set_dialog_wallpaper(dialog):
    class_name = dialog.__class__.__name__
    dialog.setStyleSheet(rf"""
        {class_name} {{
            background-image: url("{config.current_wallpaper.url}"); 
            background-position: {config.current_wallpaper.position};
        }}
    """)


def set_previewer_wallpaper(previewer):
    previewer.setStyleSheet(rf"""
        QDialog {{
            background-image: url("{config.current_wallpaper.url}"); 
            background-position: {config.current_wallpaper.position};
        }}
    """)


# todo also change wallpaper for the previewer?
#   previewer is not registered with the dialog manager
#   so we can't just grab the instance as easily as with the other dialogs
def set_wallpapers_now():
    set_main_window_wallpaper()

    for dialog_name in config.altered_dialogs:
        if dialog := get_dialog_instance_or_none(dialog_name):
            set_dialog_wallpaper(dialog)


############################################################################## web views


# Anki misuses `QColor` in python, and also in css, by calling its `name()`.
# The problem is, the return value of `name()` does not contain the alpha.
class MonstrousTransparentColor(QColor):
    def __init__(self):
        super().__init__()
        self.setAlpha(0)

    def name(self, *args, **kwargs):
        return "transparent"

monstrous_transparent_color = MonstrousTransparentColor()


@replace_method(aqt.editor.EditorWebView, "__init__")
def editor_webview_init(self, parent, editor):
    if editor.parentWindow.__class__.__name__ in config.altered_dialogs:
        self._transparent = True
    editor_webview_init.original_method(self, parent, editor)


@replace_method(aqt.webview.AnkiWebView, "get_window_bg_color")
def webview_get_window_bg_color(self, *args, **kwargs):
    transparent = getattr(self, "_transparent", False) or self.title in [
        "top toolbar",
        "main webview",
        "bottom toolbar",
        "previewer",
    ]

    if transparent:
        self.page().setBackgroundColor(Qt.GlobalColor.transparent)
        return monstrous_transparent_color
    else:
        return webview_get_window_bg_color.original_method(self, *args, **kwargs)


############################################################################## previewer


@append_to_method(aqt.browser.previewer.Previewer, "__init__")
def previewer_init(self, *_args, **_kwargs):
    set_previewer_wallpaper(self)


@append_to_method(aqt.browser.previewer.Previewer, "show")
def previewer_show(self, *_args, **_kwargs):
    self._web.setStyleSheet(r"""
        #_web { background: transparent }
    """)

############################################################# add cards and edit current


@append_to_method(aqt.addcards.AddCards, "__init__")
def add_cards_init(self, *_args, **_kwargs):
    self.form.fieldsArea.setStyleSheet(r"""
       #fieldsArea { background: transparent }
    """)


@append_to_method(aqt.editor.Editor, "setupWeb")
def editor_init(self, *_args, **_kwargs):
    dialog = self.parentWindow

    if dialog.__class__.__name__ in config.altered_dialogs:
        set_dialog_wallpaper(dialog)

        self.widget.setStyleSheet(r"""
            EditorWebView { background: transparent }
        """)


############################################################# web view css manipulations


# * `current`: the class for the currently selected deck; solid color by default
# * `zero-count`:  the class for zeros in the due cards table; barely visible by default
# * `sticky-container`: the class for a div behind the button bars and the tag bar
#    in the Editor. in night mode, these seem to have background color
# * `container-fluid`: the same but in Anki 2.1.49.
def webview_will_set_content(web_content: aqt.webview.WebContent, context):
    if isinstance(context, aqt.deckbrowser.DeckBrowser):  # noqa
        web_content.head += """<style>
            .current { background-color: #fff3 !important }
            .zero-count { color: #0005 !important }
            .night-mode .zero-count { color: #fff5 !important }
        </style>"""

    if isinstance(context, aqt.editor.Editor):
        if context.parentWindow.__class__.__name__ in config.altered_dialogs:
            web_content.head += """<style>
                body {background: none !important }
                .sticky-container, .container-fluid { background: none !important }
            </style>"""


########################################################################## configuration


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


config = Config()
config.load()


########################################################################################


def state_did_change(new_state, _old_state):
    if new_state == "deckBrowser" and config.change_wallpaper_on_deck_browser:
        config.index += 1
        set_wallpapers_now()


if anki_version >= (2, 1, 50):
    gui_hooks.theme_did_change.append(set_wallpapers_now)

gui_hooks.webview_will_set_content.append(webview_will_set_content)
gui_hooks.state_did_change.append(state_did_change)


set_wallpapers_now()
