# source/widgets.py
from __future__ import annotations

from PySide6.QtCore import QEasingCurve, Property, QRectF, QSize, Qt, QPropertyAnimation
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QAbstractButton, QLabel


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)

        self._offset = 0.0
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

        self._on_bg = QColor("#506eaa")
        self._off_bg = QColor("#2a2a30")
        self._knob = QColor("#f2f2f2")
        self._border = QColor("#2a2a30")

        self.toggled.connect(self._on_toggled)
        self._offset = 1.0 if self.isChecked() else 0.0
        self.setFixedSize(46, 24)

    def sizeHint(self) -> QSize:
        return QSize(46, 24)

    def _on_toggled(self, checked: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def get_offset(self) -> float:
        return self._offset

    def set_offset(self, v: float) -> None:
        self._offset = float(v)
        self.update()

    offset = Property(float, get_offset, set_offset)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        r = QRectF(0.5, 0.5, self.width() - 1.0, self.height() - 1.0)
        rad = r.height() / 2.0

        bg = self._on_bg if self.isChecked() else self._off_bg
        p.setPen(QPen(self._border, 1.0))
        p.setBrush(bg)
        p.drawRoundedRect(r, rad, rad)

        m = 3.0
        d = r.height() - 2 * m
        x = r.x() + m + self._offset * (r.width() - 2 * m - d)
        knob = QRectF(x, r.y() + m, d, d)

        p.setPen(Qt.NoPen)
        p.setBrush(self._knob)
        p.drawEllipse(knob)
        p.end()


class StatusPill(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedWidth(110)
        self.setText("—")
        self.set_state("off")

    def set_state(self, state: str) -> None:
        if state == "on":
            bg, bd, fg = "#23314a", "#3b4f7a", "#d6e2ff"
        elif state == "pending":
            bg, bd, fg = "#3a3424", "#7a6231", "#f3e6c8"
        elif state == "error":
            bg, bd, fg = "#3a2424", "#7a3131", "#f3c8c8"
        else:
            bg, bd, fg = "#2a2a30", "#3a3a42", "#d6d6d6"

        self.setStyleSheet(
            f"""
            QLabel {{
                background: {bg};
                border: 1px solid {bd};
                border-radius: 10px;
                padding: 4px 8px;
                color: {fg};
                font-weight: 600;
            }}
            """
        )

    def setTextAndState(self, text: str, state: str) -> None:
        self.setText(text)
        self.set_state(state)


class ElideLabel(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def paintEvent(self, event) -> None:
        fm = QFontMetrics(self.font())
        txt = fm.elidedText(self.text(), Qt.ElideRight, max(10, self.width() - 6))
        old = self.text()
        try:
            self.setText(txt)
            super().paintEvent(event)
        finally:
            self.setText(old)
