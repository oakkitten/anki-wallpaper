import aqt
import aqt.browser.previewer
import aqt.deckbrowser
import aqt.editor
import aqt.theme
import aqt.webview
from aqt import gui_hooks
from aqt.qt import Qt, QColor, QAction

from .configuration import Config, run_on_configuration_change
from .tools import append_to_method, replace_method, prepend_to_method
from .tools import get_dialog_instance_or_none


anki_version = tuple(int(segment) for segment in aqt.appVersion.split("."))


ALTERED_DIALOGS_CLASS_NAMES = {
    "AddCards",
    "EditCurrent",
    "Edit",
}


ALTERED_DIALOGS_DIALOG_MANAGER_TAGS = {
    "AddCards",
    "EditCurrent",
    "foosoft.ankiconnect.Edit",
}


# This also removes the weird border below the menu bar that is present on Anki 2.1.50.
# It is not changed with the theme for some reason.
def set_main_window_wallpaper():
    aqt.mw.setStyleSheet(rf"""
        QMainWindow {{
            background-image: url("{config.current_wallpaper.url}"); 
            background-position: {config.current_wallpaper.position};
        }}
        
        QMenuBar {{ 
            background: transparent;
            border: none; 
        }}
        
        #centralwidget {{  background: transparent; }}
    """)

def unset_main_window_wallpaper():
    aqt.mw.setStyleSheet("")


def set_dialog_wallpaper(dialog):
    dialog.setStyleSheet(rf"""
        {dialog.__class__.__name__} {{
            background-image: url("{config.current_wallpaper.url}"); 
            background-position: {config.current_wallpaper.position};
        }}
    """)

def unset_dialog_wallpaper(dialog):
    dialog.setStyleSheet("")


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
    if config.is_enabled.for_main_window:
        set_main_window_wallpaper()
    else:
        unset_main_window_wallpaper()

    for dialog_tag in ALTERED_DIALOGS_DIALOG_MANAGER_TAGS:
        if dialog := get_dialog_instance_or_none(dialog_tag):
            if config.is_enabled.for_dialog(class_name=dialog.__class__.__name__):
                set_dialog_wallpaper(dialog)
            else:
                unset_dialog_wallpaper(dialog)


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


@prepend_to_method(aqt.editor.EditorWebView, "__init__")
def editor_webview_init(self, _parent, editor):
    if editor.parentWindow.__class__.__name__ in ALTERED_DIALOGS_CLASS_NAMES:
        self._transparent = True


@replace_method(aqt.webview.AnkiWebView, "get_window_bg_color")
def webview_get_window_bg_color(self, *args, **kwargs):
    transparent = getattr(self, "_transparent", False) or self.title in [
        "top toolbar",
        "main webview",
        "bottom toolbar",
        "previewer"
    ]

    if transparent:
        self.page().setBackgroundColor(Qt.GlobalColor.transparent)
        return monstrous_transparent_color
    else:
        return webview_get_window_bg_color.original_method(self, *args, **kwargs)


############################################################################## previewer


@append_to_method(aqt.browser.previewer.Previewer, "__init__")
def previewer_init(self, *_args, **_kwargs):
    if config.is_enabled.for_previewer:
        set_previewer_wallpaper(self)


@append_to_method(aqt.browser.previewer.Previewer, "show")
def previewer_show(self, *_args, **_kwargs):
    self._web.setStyleSheet(r"""
        #_web { background: transparent }
    """)


####################################################### add cards, edit current and edit


@append_to_method(aqt.addcards.AddCards, "__init__")
def add_cards_init(self, *_args, **_kwargs):
    self.form.fieldsArea.setStyleSheet(r"""
       #fieldsArea { background: transparent }
    """)


@append_to_method(aqt.editor.Editor, "setupWeb")
def editor_init(self, *_args, **_kwargs):
    dialog = self.parentWindow
    dialog_class_name = dialog.__class__.__name__

    if dialog_class_name in ALTERED_DIALOGS_CLASS_NAMES:
        self.widget.setStyleSheet(r"""
            EditorWebView { background: transparent }
        """)

        if config.is_enabled.for_dialog(dialog_class_name):
            set_dialog_wallpaper(dialog)


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
        if context.parentWindow.__class__.__name__ in ALTERED_DIALOGS_CLASS_NAMES:
            web_content.head += """<style>
                body {background: none !important }
                .sticky-container, .container-fluid { background: none !important }
            </style>"""


########################################################################################


def next_wallpaper():
    config.next_wallpaper()
    set_wallpapers_now()

# View menu on Anki 2.1.50+, Tools menu if View menu not available
def setup_next_wallpaper_menu():
    menu_next_wallpaper = QAction("Next wallpaper", aqt.mw, shortcut="Ctrl+Shift+W")  # noqa
    menu_next_wallpaper.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
    menu_next_wallpaper.triggered.connect(next_wallpaper)  # noqa

    try:
        menu = aqt.mw.form.menuqt_accel_view
    except AttributeError:
        menu = aqt.mw.form.menuTools

    menu.addSeparator()
    menu.addAction(menu_next_wallpaper)


config = Config()
config.load()


@run_on_configuration_change
def on_configuration_change():
    config.load()
    set_wallpapers_now()


if anki_version >= (2, 1, 50):
    gui_hooks.theme_did_change.append(set_wallpapers_now)

gui_hooks.webview_will_set_content.append(webview_will_set_content)


setup_next_wallpaper_menu()
set_wallpapers_now()
