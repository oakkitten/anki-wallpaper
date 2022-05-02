import aqt
from aqt.qt import QColor, QWindow, QMainWindow

from tests.conftest import wait_until


def get_color(window: QWindow, x: int, y: int) -> str:
    color = window.screen().grabWindow(window.winId()).toImage().pixel(x, y)
    return QColor(color).name()


def set_main_window_dimensions(window: QMainWindow, width: int, height: int):
    window.setFixedWidth(width)
    window.setFixedHeight(height)


########################################################################################


def test_main_window(setup):
    set_main_window_dimensions(aqt.mw, 500, 500)
    wait_until(lambda: get_color(aqt.mw, 5, 47) == "#aaaaaa")  # gray line below upper links
    assert get_color(aqt.mw, 5, 5) == "#eeebe7"  # menu
    assert get_color(aqt.mw, 5, 40) == "#eeebe7"  # links
    assert get_color(aqt.mw, 5, 280) == "#eeebe7"  # main area
    assert get_color(aqt.mw, 5, 490) == "#e5dfd9"  # bottom area
