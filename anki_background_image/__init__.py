import aqt
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


def set_edit_current_background_image(edit_current, image_path):
    edit_current.setStyleSheet(rf"""
        EditCurrent {{
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

    if edit_current := get_dialog_instance_or_none("EditCurrent"):
        set_edit_current_background_image(edit_current, image_path)


############################################################################## web views


def is_transparent_webview(webview: aqt.webview.AnkiWebView) -> bool:
    if webview.title in [
        "top toolbar",
        "main webview",
        "bottom toolbar",
        "previewer",
    ]:
        return True

    if webview.title == "editor":
        if parent := webview.parent():
            if parent.__class__.__name__ == "EditCurrent":
                return True

    return False


@append_to_method(aqt.webview.AnkiWebView, "__init__")
def webview_init(self, *_args, **_kwargs):
    if is_transparent_webview(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(True)
        self.setWindowFlags(Qt.FramelessWindowHint)


@replace_method(aqt.webview.AnkiWebView, "get_window_bg_color")
def webview_get_window_bg_color(self, *args, **kwargs):
    if is_transparent_webview(self):
        self.page().setBackgroundColor(Qt.transparent)
        return type("FakeColor", (QColor,), {'name': lambda self: 'transparent'})()
        #return Qt.transparent
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


########################################################################### edit current


@append_to_method(aqt.editcurrent.EditCurrent, "__init__")
def edit_current_init(self, *_args, **_kwargs):
    set_edit_current_background_image(self, get_current_image_path())

    self.editor.widget.setStyleSheet(r"""
        EditorWebView { background: transparent }
    """)

########################################################################################


def theme_did_change():
    set_background_images_now(get_current_image_path())


gui_hooks.theme_did_change.append(theme_did_change)


set_background_images_now(get_current_image_path())