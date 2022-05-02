import aqt
from aqt.qt import QColor, QWindow, QMainWindow

from tests.conftest import wait


def get_color(window: QWindow, x: int, y: int) -> str:
    color = window.screen().grabWindow(window.winId()).toImage().pixel(x, y)
    return QColor(color).name()


def set_main_window_dimensions(window: QMainWindow, width: int, height: int):
    window.setFixedWidth(width)
    window.setFixedHeight(height)


def test_main_window(setup):
    window = aqt.mw
    set_main_window_dimensions(window, 500, 500)
    wait(5)
    assert get_color(window, 5, 1) == "#eeebe7"
    assert get_color(window, 1, 40) == "#eeebe7"
    assert get_color(window, 1, 490) == "#e5dfd9"
