import aqt
from aqt.qt import QColor, QWindow, QWidget, QDialog

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
    set_window_dimensions(window, 500, 500)
    wait_until(lambda: get_color(window, 5, 47) == "#aaaaaa")  # gray line below upper links
    assert get_color(window, 5, 5) == "#eeebe7"  # menu
    assert get_color(window, 5, 40) == "#eeebe7"  # links
    assert get_color(window, 5, 280) == "#eeebe7"  # main area
    assert get_color(window, 5, 490) == "#e5dfd9"  # bottom area


def test_add_cards_dialog(setup):
    dialog = aqt.dialogs.open("AddCards", aqt.mw)
    set_window_dimensions(dialog, 500, 500)
    wait_until(lambda: get_color(dialog, 330, 160) == "#ffffff")  # field1
    assert get_color(dialog, 5, 5) == "#eeebe7"  # edge
    assert get_color(dialog, 270, 80) == "#eeebe7"  # buttons area
    assert get_color(dialog, 270, 270) == "#eeebe7"  # main area
    assert get_color(dialog, 270, 430) == "#eeebe7"  # tags area
    assert get_color(dialog, 5, 490) == "#e5dfd9"  # bottom area
