import os

import aqt
import aqt.browser.previewer
import aqt.deckbrowser
import aqt.editor
import aqt.theme
import aqt.webview
from aqt import gui_hooks
from aqt.qt import Qt, QColor
from aqt.utils import showWarning

from .anki_tool import get_dialog_instance_or_none
from .tools import append_to_method, replace_method


anki_version = tuple(int(segment) for segment in aqt.appVersion.split("."))


def set_main_window_background_image():
    aqt.mw.setStyleSheet(rf"""
        QMainWindow {{
            background-image: url("{config.current_image_path}"); 
            background-position: center;
        }}
        QMenuBar {{
            background: transparent;
        }}
        #centralwidget {{ 
            background: transparent; 
        }}
    """)


def set_dialog_background_image(dialog):
    class_name = dialog.__class__.__name__
    dialog.setStyleSheet(rf"""
        {class_name} {{
            background-image: url("{config.current_image_path}"); 
            background-position: center;
        }}
    """)


def set_previewer_background_image(previewer):
    previewer.setStyleSheet(rf"""
        QDialog {{
            background-image: url("{config.current_image_path}"); 
            background-position: center;
        }}
    """)


def set_background_images_now():
    set_main_window_background_image()

    for dialog_name in config.altered_dialogs:
        if dialog := get_dialog_instance_or_none(dialog_name):
            set_dialog_background_image(dialog)


############################################################################## web views


@replace_method(aqt.editor.EditorWebView, "__init__")
def editor_webview_init(self, parent, editor):
    if editor.parentWindow.__class__.__name__ in config.altered_dialogs:
        self._transparent = True
    editor_webview_init.original_method(self, parent, editor)


class NamedTransparentColor(QColor):
    def __init__(self):
        super().__init__()
        self.setAlpha(0)

    def name(self):
        return "transparent"

transparent_color = NamedTransparentColor()


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
        return transparent_color
    else:
        return webview_get_window_bg_color.original_method(self, *args, **kwargs)


############################################################################## previewer


@append_to_method(aqt.browser.previewer.Previewer, "__init__")
def previewer_init(self, *_args, **_kwargs):
    set_previewer_background_image(self)


@append_to_method(aqt.browser.previewer.Previewer, "show")
def previewer_show(self, *_args, **_kwargs):
    self._web.setStyleSheet(r"""
        #_web { background: transparent }
    """)

############################################################################## add cards


@append_to_method(aqt.addcards.AddCards, "__init__")
def add_cards_init(self, *_args, **_kwargs):
    self.form.fieldsArea.setStyleSheet(r"""
       #fieldsArea { background: transparent }
    """)


############################################################# add cards and edit current


@append_to_method(aqt.editor.Editor, "setupWeb")
def editor_init(self, *_args, **_kwargs):
    dialog = self.parentWindow

    if dialog.__class__.__name__ in config.altered_dialogs:
        set_dialog_background_image(dialog)

        self.widget.setStyleSheet(r"""
            EditorWebView { background: transparent }
        """)


########################################################################### deck browser


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


########################################################################################


# noinspection PyAttributeOutsideInit
class Config:
    def reload(self):
        self.data = aqt.mw.addonManager.getConfig(__name__)

        errors = []
        for path in [self.data["dark_mode_image_path"], self.data["light_mode_image_path"]]:
            if not os.path.exists(path):
                errors.append(f"Image does not exist: '{path}'")
            if '"' in path:
                errors.append(f"Image path must not contain quotation marks: '{path}'")

        if errors:
            errors_str = '\n'.join(errors)
            showWarning(
                title="Background Image",
                text="There were issues with some of the background images. "
                     "Expect things to break.\n\n"
                     f"{errors_str}\n\n"
                     "You can change images in "
                     "Tools → Add-ons → Background image → Config.",
                help=None,  # noqa
            )

    @property
    def current_image_path(self):
        dark = aqt.theme.theme_manager.night_mode
        return self.data["dark_mode_image_path" if dark else "light_mode_image_path"]

    @property
    def altered_dialogs(self):
        return ["AddCards", "EditCurrent"]

config = Config()
config.reload()


########################################################################################


def theme_did_change():
    set_background_images_now()


if anki_version >= (2, 1, 50):
    gui_hooks.theme_did_change.append(theme_did_change)

gui_hooks.webview_will_set_content.append(webview_will_set_content)

set_background_images_now()
