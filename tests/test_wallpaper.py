import os
import sys
import re
from contextlib import contextmanager
from dataclasses import dataclass
from unittest.mock import MagicMock

import aqt
import pytest
from _pytest.monkeypatch import MonkeyPatch
from aqt.addons import AddonsDialog, ConfigEditor
from aqt.qt import QColor, QWidget, QImage

from tests.anki_tools import move_main_window_to_state, anki_version
from tests.conftest import wait_until, get_dialog_instance, wait


image_save_folder = os.getcwd()


def get_screenshot(window: QWidget) -> QImage:
    return window.grab().toImage()


def get_color(obj: "QWidget | QImage", x: int, y: int) -> str:
    if isinstance(obj, QWidget):
        obj = get_screenshot(obj)
    return QColor(obj.pixel(x, y)).name()


def save_screenshot(window: QWidget, image_title: str):
    image = get_screenshot(window)
    image_path = os.path.join(image_save_folder, image_title + ".png")
    image.save(image_path)
    print(f":: saved image: {image_path}")


@contextmanager
def screenshot_saved_on_error(window: QWidget, image_title: str = None):
    if image_title is None:
        calling_method_name = sys._getframe().f_back.f_back.f_code.co_name  # noqa
        window_class = window.__class__.__name__
        image_title = calling_method_name + "_" + window_class
    try:
        yield
    except Exception:
        save_screenshot(window, image_title)
        raise


def set_window_dimensions(window: QWidget, width: int, height: int):
    window.resize(width, height)


################################### get windows and wait for them to become fully loaded


def get_main_window():
    window = aqt.mw
    window.resize(500, 500)

    # looking for the gray line below upper links.
    # it might have different colors, so just see if there's anything at all
    def main_window_ready():
        screenshot = get_screenshot(window)
        different_colors = {get_color(screenshot, 5, 40 + x) for x in range(16)}
        return len(different_colors) > 1

    with screenshot_saved_on_error(window):
        wait_until(main_window_ready)

    return window


def get_add_cards_dialog():
    dialog = aqt.dialogs.open("AddCards", aqt.mw)
    dialog.resize(500, 500)

    with screenshot_saved_on_error(dialog):
        wait_until(lambda: get_color(dialog, 330, 230) == "#ffffff")  # field2

    return dialog


def get_edit_current_dialog():
    move_main_window_to_state("review")
    dialog = aqt.dialogs.open("EditCurrent", aqt.mw)
    dialog.resize(500, 500)

    with screenshot_saved_on_error(dialog):
        wait_until(lambda: get_color(dialog, 330, 200) == "#ffffff")  # field2

    return dialog


def get_previewer():
    browser = aqt.dialogs.open("Browser", aqt.mw)
    wait_until(lambda: browser.editor.note is not None)

    browser.onTogglePreview()
    previewer = browser._previewer
    previewer.resize(500, 500)

    with screenshot_saved_on_error(previewer):
        wait_until(lambda: get_color(previewer, 30, 30) == "#ff0000")  # our red marker

    return previewer


########################################################################################


def test_main_window(setup):
    window = get_main_window()

    with screenshot_saved_on_error(window):
        assert get_color(window, 5, 5) == "#eeebe7"  # menu
        assert get_color(window, 5, 40) == "#eeebe7"  # links
        assert get_color(window, 5, 280) == "#eeebe7"  # main area
        assert get_color(window, 5, 490) == "#e5dfd9"  # bottom area


# on Anki 2.1.49 tag area is an input field and has white background
# on Anki 2.1.49+ it's a special thing with tags and has transparent background
def test_add_cards_dialog(setup):
    dialog = get_add_cards_dialog()

    with screenshot_saved_on_error(dialog):
        assert get_color(dialog, 5, 5) == "#eeebe7"  # edge
        assert get_color(dialog, 270, 80) == "#eeebe7"  # buttons area
        assert get_color(dialog, 270, 270) == "#eeebe7"  # main area
        if anki_version >= (2, 1, 50):
            assert get_color(dialog, 270, 430) == "#eeebe7"  # tags area
        assert get_color(dialog, 5, 490) == "#e5dfd9"  # bottom area


def test_edit_current_dialog(setup):
    dialog = get_edit_current_dialog()

    with screenshot_saved_on_error(dialog):
        assert get_color(dialog, 5, 5) == "#eeebe7"  # edge
        assert get_color(dialog, 270, 60) == "#eeebe7"  # buttons area
        assert get_color(dialog, 270, 270) == "#eeebe7"  # main area
        if anki_version >= (2, 1, 50):
            assert get_color(dialog, 270, 440) == "#eeebe7"  # tags area
        assert get_color(dialog, 5, 490) == "#e5dfd9"  # bottom area


def test_previewer(setup):
    previewer = get_previewer()

    with screenshot_saved_on_error(previewer):
        assert get_color(previewer, 5, 5) == "#eeebe7"  # edge
        assert get_color(previewer, 5, 490) == "#e5dfd9"  # bottom area


########################################################################################


@contextmanager
def all_windows_set_up():
    main_window = get_main_window()
    add_cards_dialog = get_add_cards_dialog()
    edit_current = get_edit_current_dialog()

    def get_colors():
        return [
            get_color(window, 5, 5) for window in (
                main_window, add_cards_dialog, edit_current
            )
        ]

    with screenshot_saved_on_error(main_window), \
         screenshot_saved_on_error(add_cards_dialog), \
         screenshot_saved_on_error(edit_current):
        yield get_colors



def test_next_wallpaper(setup):
    with all_windows_set_up() as get_colors:
        assert get_colors() == ["#eeebe7"] * 3

        setup.anki_wallpaper.next_wallpaper()
        wait_until(lambda: get_colors() == ["#ebebeb"] * 3)

        setup.anki_wallpaper.next_wallpaper()
        wait_until(lambda: get_colors() == ["#eeebe7"] * 3)


@pytest.mark.skipif(anki_version < (2, 1, 50), reason="not applicable to Anki < 2.1.50")
def test_theme_change(setup):
    from aqt.theme import Theme

    with all_windows_set_up() as get_colors:
        assert get_colors() == ["#eeebe7"] * 3

        aqt.mw.set_theme(Theme.DARK)
        wait_until(lambda: get_colors() == ["#303030"] * 3)

        aqt.mw.set_theme(Theme.LIGHT)
        wait_until(lambda: get_colors() == ["#eeebe7"] * 3)


########################################################################################


@contextmanager
def editing_config():
    addon = "anki_wallpaper"
    config = aqt.mw.addonManager.getConfig(addon)

    addons_dialog = AddonsDialog(aqt.mw.addonManager)
    config_editor = ConfigEditor(addons_dialog, addon, config)

    class Editor:
        @property
        def text(self):
            return config_editor.form.editor.toPlainText()

        @text.setter
        def text(self, new_text):
            assert new_text != self.text
            config_editor.form.editor.setPlainText(new_text)

    try:
        yield Editor()
    finally:
        config_editor.accept()
        addons_dialog.accept()


@dataclass
class Called:
    mock: MagicMock

    @property
    def times(self):
        return self.mock.call_count

    @property
    def first_argument(self):
        return self.mock.call_args_list[0].args[0]

    @property
    def text_argument(self):
        return self.mock.call_args_list[0].kwargs["text"]


@contextmanager
def method_mocked(*args):
    with MonkeyPatch().context() as context:
        mock = MagicMock()
        context.setattr(*args, mock)
        yield Called(mock)


def test_anki_freaks_out_with_invalid_json_schema(setup):
    with method_mocked(aqt.addons, "showInfo") as called:
        with editing_config() as editor:
            editor.text = editor.text.replace("a", "b")
        assert called.times == 1
        assert "is a required property" in called.first_argument

    with method_mocked(aqt.addons, "showInfo") as called:
        with editing_config() as editor:
            editor.text = editor.text.replace("edit_current", "edit_kitten")
        assert called.times == 1
        assert "is not one of" in called.first_argument


def test_anki_freaks_out_with_inaccessible_folder(setup):
    with method_mocked(setup.anki_wallpaper.configuration, "showWarning") as called:
        with editing_config() as editor:
            editor.text = re.sub(r'"/[^"]+"', '"/root/"', editor.text)
        assert called.times == 1
        assert "Permission denied" in called.text_argument


def test_anki_freaks_out_with_not_existing_folder(setup):
    with method_mocked(setup.anki_wallpaper.configuration, "showWarning") as called:
        with editing_config() as editor:
            editor.text = re.sub(r'"/[^"]+"', '"/owo whats this/"', editor.text)
        assert called.times == 1
        assert "No such file" in called.text_argument


def test_anki_freaks_out_with_wanted_files_missing(setup, tmpdir):
    with method_mocked(setup.anki_wallpaper.configuration, "showWarning") as called:
        with editing_config() as editor:
            editor.text = re.sub(r'"/[^"]+"', f'"{tmpdir.strpath}"', editor.text)
        assert called.times == 1
        assert "does not contain dark wallpapers" in called.text_argument
