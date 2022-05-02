import aqt
from aqt.qt import QColor, QWindow, QWidget

from tests.anki_tools import move_main_window_to_state, anki_version
from tests.conftest import wait_until, wait


def get_color(window: QWindow, x: int, y: int) -> str:
    color = window.screen().grabWindow(window.winId()).toImage().pixel(x, y)
    return QColor(color).name()


def set_window_dimensions(window: QWidget, width: int, height: int):
    window.setFixedWidth(width)
    window.setFixedHeight(height)


########################################################################################


def test_main_window(setup):
    window = aqt.mw

    # looking for the gray line below upper links
    def main_window_ready():
        for x in range(16):
            if get_color(window, 5, 40 + x) in ["#aaaaaa", "#ababab"]:
                return True
        return False

    set_window_dimensions(window, 500, 500)
    wait_until(main_window_ready)
    assert get_color(window, 5, 5) == "#eeebe7"  # menu
    assert get_color(window, 5, 40) == "#eeebe7"  # links
    assert get_color(window, 5, 280) == "#eeebe7"  # main area
    assert get_color(window, 5, 490) == "#e5dfd9"  # bottom area


# on Anki 2.1.49 tag area is an input field and has white background
# on Anki 2.1.49+ it's a special thing with tags and has transparent background
def test_add_cards_dialog(setup):
    dialog = aqt.dialogs.open("AddCards", aqt.mw)
    set_window_dimensions(dialog, 500, 500)
    wait_until(lambda: get_color(dialog, 330, 160) == "#ffffff")  # field1
    assert get_color(dialog, 5, 5) == "#eeebe7"  # edge
    assert get_color(dialog, 270, 80) == "#eeebe7"  # buttons area
    assert get_color(dialog, 270, 270) == "#eeebe7"  # main area
    if anki_version >= (2, 1, 50):
        assert get_color(dialog, 270, 430) == "#eeebe7"  # tags area
    assert get_color(dialog, 5, 490) == "#e5dfd9"  # bottom area


def test_edit_current_dialog(setup):
    move_main_window_to_state("review")
    dialog = aqt.dialogs.open("EditCurrent", aqt.mw)
    set_window_dimensions(dialog, 500, 500)
    wait_until(lambda: get_color(dialog, 330, 130) == "#ffffff")  # field1
    assert get_color(dialog, 5, 5) == "#eeebe7"  # edge
    assert get_color(dialog, 270, 60) == "#eeebe7"  # buttons area
    assert get_color(dialog, 270, 250) == "#eeebe7"  # main area
    if anki_version >= (2, 1, 50):
        assert get_color(dialog, 270, 440) == "#eeebe7"  # tags area
    assert get_color(dialog, 5, 490) == "#e5dfd9"  # bottom area
