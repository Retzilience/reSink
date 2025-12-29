from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from widgets import ElideLabel


@dataclass(frozen=True)
class SinkRowModel:
    name: str
    description: str
    is_virtual: bool
    is_default: bool


class SinkRow(QWidget):
    selection_changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("RowCard")
        self.setProperty("kind", "physical")
        self.setProperty("selected", False)
        self.setProperty("default", False)

        self._model: SinkRowModel | None = None
        self._selected = False

        self.desc_lbl = ElideLabel()
        self.desc_lbl.setAlignment(Qt.AlignCenter)
        self.desc_lbl.setObjectName("SinkTitle")

        self.kind_pill = QLabel("—")
        self.kind_pill.setObjectName("KindPill")
        self.kind_pill.setAlignment(Qt.AlignCenter)
        self.kind_pill.setProperty("kind", "physical")

        self.name_lbl = ElideLabel()
        self.name_lbl.setAlignment(Qt.AlignCenter)
        self.name_lbl.setObjectName("SinkName")

        self.select_bar = QLabel("")
        self.select_bar.setObjectName("SelectBar")
        self.select_bar.setAlignment(Qt.AlignCenter)
        self.select_bar.setProperty("sel", False)
        self.select_bar.setProperty("kind", "virtual")

        lay = QVBoxLayout()
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)
        self.setLayout(lay)

        lay.addWidget(self.desc_lbl, 0)
        lay.addWidget(self.kind_pill, 0, Qt.AlignHCenter)
        lay.addWidget(self.name_lbl, 0)
        lay.addWidget(self.select_bar, 0)

        self.setCursor(Qt.ArrowCursor)

    def model(self) -> SinkRowModel | None:
        return self._model

    def is_selected(self) -> bool:
        return bool(self._selected)

    def set_selected(self, v: bool) -> None:
        if self._model is None:
            return
        if not self._model.is_virtual:
            self._selected = False
            self._sync_state()
            return

        self._selected = bool(v)
        self._sync_state()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self._model is not None and self._model.is_virtual:
                self._selected = not self._selected
                self._sync_state()
                self.selection_changed.emit()
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def set_model(self, m: SinkRowModel) -> None:
        self._model = m

        self.desc_lbl.setText(m.description)
        self.name_lbl.setText(m.name)

        kind = "virtual" if m.is_virtual else "physical"
        self.setProperty("kind", kind)
        self.setProperty("default", bool(m.is_default))

        if m.is_virtual:
            self.kind_pill.setText("VIRTUAL")
            self.kind_pill.setProperty("kind", "virtual")
            self.select_bar.setVisible(True)
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.kind_pill.setText("PHYSICAL")
            self.kind_pill.setProperty("kind", "physical")
            self.select_bar.setVisible(False)
            self._selected = False
            self.setCursor(Qt.ArrowCursor)

        self.setToolTip(f"{m.description}\n{m.name}")
        self._sync_state()

    def _sync_state(self) -> None:
        m = self._model
        if m is None:
            return

        if m.is_virtual:
            self.setProperty("selected", bool(self._selected))
            self.select_bar.setProperty("sel", bool(self._selected))
            self.select_bar.setText("Selected" if self._selected else "Not Selected")
        else:
            self.setProperty("selected", False)

        self.style().unpolish(self)
        self.style().polish(self)

        self.kind_pill.style().unpolish(self.kind_pill)
        self.kind_pill.style().polish(self.kind_pill)

        if m.is_virtual:
            self.select_bar.style().unpolish(self.select_bar)
            self.select_bar.style().polish(self.select_bar)

        self.update()
