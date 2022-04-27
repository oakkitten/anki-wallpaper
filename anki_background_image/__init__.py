import aqt
import aqt.editor
import aqt.browser.previewer
import aqt.webview
from aqt import gui_hooks

from aqt.qt import Qt, QColor

from .anki_tool import get_dialog_instance_or_none
from .tools import append_to_method, replace_method


def get_current_image_path() -> str:
    return ""


########################################################################################


def set_main_window_background_image(image_path):
    aqt.mw.setStyleSheet(rf"""
        QMainWindow {{
            background-image: url("{image_path}"); 
            background-position: center;
        }}
        QMenuBar {{
            background: transparent;
        }}
        #centralwidget {{ 
            background: transparent; 
        }}
    """)


def set_dialog_background_image(dialog, image_path):
    class_name = dialog.__class__.__name__
    dialog.setStyleSheet(rf"""
        {class_name} {{
            background-image: url("{image_path}"); 
            background-position: center;
        }}
    """)


def set_previewer_background_image(previewer, image_path):
    previewer.setStyleSheet(rf"""
        QDialog {{
            background-image: url("{image_path}"); 
            background-position: center;
        }}
    """)


def set_background_images_now(image_path):
    set_main_window_background_image(image_path)

    for dialog_name in ["AddCards", "EditCurrent"]:
        if dialog := get_dialog_instance_or_none(dialog_name):
            set_dialog_background_image(dialog, image_path)


############################################################################## web views


@replace_method(aqt.editor.EditorWebView, "__init__")
def editor_webview_init(self, parent, editor):
    if editor.parentWindow.__class__.__name__ in ["AddCards", "EditCurrent"]:
        self._transparent = True
    editor_webview_init.original_method(self, parent, editor)


class FakeTransparentColor(QColor):
    def name(self):
        return "transparent"

fake_transparent_color = FakeTransparentColor()


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
        return fake_transparent_color
    else:
        return webview_get_window_bg_color.original_method(self, *args, **kwargs)


############################################################################## previewer


@append_to_method(aqt.browser.previewer.Previewer, "__init__")
def previewer_init(self, *_args, **_kwargs):
    set_previewer_background_image(self, get_current_image_path())


@append_to_method(aqt.browser.previewer.Previewer, "show")
def previewer_show(self, *_args, **_kwargs):
    self._web.setStyleSheet(r"""
        QWidget { background: transparent }
        QMenu { background: #f0f0f0 }
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

    if dialog.__class__.__name__ in ["AddCards", "EditCurrent"]:
        set_dialog_background_image(dialog, get_current_image_path())

        self.widget.setStyleSheet(r"""
            EditorWebView { background: transparent }
        """)


########################################################################################


def theme_did_change():
    set_background_images_now(get_current_image_path())


gui_hooks.theme_did_change.append(theme_did_change)


set_background_images_now(get_current_image_path())
