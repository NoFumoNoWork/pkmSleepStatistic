"""Global hotkey Ctrl+Alt+P on Windows."""

from __future__ import annotations

import sys
from typing import Callable, Optional

from PySide6.QtCore import QAbstractNativeEventFilter, QByteArray

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    WM_HOTKEY = 0x0312
    VK_P = 0x50
    HOTKEY_ID = 0xA5B1


class GlobalHotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback: Callable[[], None]) -> None:
        super().__init__()
        self._callback = callback
        self._registered = False

    def register(self) -> bool:
        if sys.platform != "win32":
            return False
        if self._registered:
            return True
        ok = user32.RegisterHotKey(
            None,
            HOTKEY_ID,
            MOD_CONTROL | MOD_ALT,
            VK_P,
        )
        self._registered = bool(ok)
        return self._registered

    def unregister(self) -> None:
        if sys.platform == "win32" and self._registered:
            user32.UnregisterHotKey(None, HOTKEY_ID)
            self._registered = False

    def nativeEventFilter(self, event_type: QByteArray, message: int) -> tuple[bool, int]:
        if sys.platform != "win32":
            return False, 0
        if event_type.data() != b"windows_generic_MSG":
            return False, 0
        msg = wintypes.MSG.from_address(int(message))
        if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
            self._callback()
            return True, 0
        return False, 0


def setup_global_hotkey(app, callback: Callable[[], None]) -> Optional[GlobalHotkeyFilter]:
    if sys.platform != "win32":
        return None
    filt = GlobalHotkeyFilter(callback)
    if filt.register():
        app.installNativeEventFilter(filt)
        return filt
    return None
