from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

import pulsectl

from resink_backend import (
    create_virtual_sink,
    set_default_sink,
    suggest_resink_name,
    wait_for_sink_to_appear,
)


class CreateVirtualSinkDialog(QDialog):
    """
    I create a virtual sink and optionally set it as default.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create virtual sink")
        self.setModal(True)
        self.setSizeGripEnabled(False)

        outer = QVBoxLayout()
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(12)
        outer.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(outer)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        outer.addLayout(form)

        try:
            suggested = suggest_resink_name()
        except pulsectl.PulseError:
            suggested = "reSink"

        self.sink_name_input = QLineEdit(suggested)
        self.sink_name_input.setMinimumWidth(360)
        form.addRow("Sink name:", self.sink_name_input)

        self.sample_rate_input = QSpinBox()
        self.sample_rate_input.setRange(16000, 192000)
        self.sample_rate_input.setValue(48000)
        self.sample_rate_input.setMinimumWidth(180)
        self.sample_rate_input.setAlignment(Qt.AlignRight)
        self.sample_rate_input.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        form.addRow("Sample rate (Hz):", self.sample_rate_input)

        self.make_default_checkbox = QCheckBox("Make default")
        form.addRow("", self.make_default_checkbox)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        create_btn = QPushButton("Create")
        create_btn.setObjectName("Primary")
        create_btn.clicked.connect(self._create_clicked)
        btns.addWidget(create_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)

        btns.addStretch(1)
        outer.addLayout(btns)

    def _create_clicked(self) -> None:
        name = self.sink_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid name", "Sink name cannot be empty.")
            return

        sr = int(self.sample_rate_input.value())
        make_default = bool(self.make_default_checkbox.isChecked())

        try:
            create_virtual_sink(name=name, sample_rate=sr)
            wait_for_sink_to_appear(name)
        except Exception as e:
            QMessageBox.critical(self, "Create failed", f"Failed to create sink.\n\n{e}")
            return

        if make_default:
            try:
                set_default_sink(name)
            except Exception as e:
                QMessageBox.warning(self, "Default failed", f"Failed to set default sink.\n\n{e}")

        self.accept()
