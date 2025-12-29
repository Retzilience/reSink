# source/dialogs_patchbay_settings.py
from __future__ import annotations

import shutil

from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from config_store import ConfigStore
from patchbay import find_asyphon_launch_argv


class PatchbaySettingsDialog(QDialog):
    """
    I store a patchbay launcher choice.
    """

    def __init__(self, store: ConfigStore, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Patchbay settings")
        self.setMinimumSize(520, 260)

        self.store = store
        self.config = self.store.load()

        # I keep insertion order here because it is also the UI order.
        self.applications: dict[str, tuple[str, str]] = {
            "asyphon": ("aSyphon", ""),  # installed check is config-based, not PATH-based
            "qpwgraph": ("qpwgraph", "qpwgraph"),
            "helvum": ("helvum", "helvum"),
            "patchance": ("patchance", "patchance"),
        }

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        self.setLayout(layout)

        form = QFormLayout()
        layout.addLayout(form)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.radio_buttons: dict[str, QRadioButton] = {}

        for key, (label, exe) in self.applications.items():
            rb = QRadioButton(label)

            if key == "asyphon":
                installed = find_asyphon_launch_argv() is not None
                rb.setEnabled(installed)
                if not installed:
                    rb.setToolTip("aSyphon is not available (no asyphon.cfg with a valid [App] last_exe_path).")
            else:
                installed = shutil.which(exe) is not None
                rb.setEnabled(installed)
                if not installed:
                    rb.setToolTip(f"{label} is not installed.")

            self.radio_buttons[key] = rb
            self.button_group.addButton(rb)
            form.addRow(rb)

        self.custom_radio = QRadioButton("custom")
        self.button_group.addButton(self.custom_radio)
        form.addRow(self.custom_radio)

        self.custom_edit = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_custom)
        browse = QHBoxLayout()
        browse.setSpacing(8)
        browse.addWidget(self.custom_edit)
        browse.addWidget(browse_btn)
        form.addRow("Custom path:", browse)

        selected_app = (self.config.get("Patchbay", "selected_app", fallback="") or "").strip()
        custom_path = (self.config.get("Patchbay", "custom_path", fallback="") or "").strip()

        done_select = False

        if selected_app in self.radio_buttons:
            rb = self.radio_buttons.get(selected_app)
            if rb is not None and rb.isEnabled():
                rb.setChecked(True)
                done_select = True

        if selected_app == "custom":
            self.custom_radio.setChecked(True)
            self.custom_edit.setText(custom_path)
            done_select = True

        if not done_select:
            for k in self.applications.keys():
                rb = self.radio_buttons.get(k)
                if rb is not None and rb.isEnabled():
                    rb.setChecked(True)
                    done_select = True
                    break

        if not done_select:
            self.custom_radio.setChecked(True)

        self._toggle_custom_edit()
        self.custom_radio.toggled.connect(self._toggle_custom_edit)
        for rb in self.radio_buttons.values():
            rb.toggled.connect(self._toggle_custom_edit)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("Primary")
        save_btn.clicked.connect(self._save)
        btns.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)

        btns.addStretch(1)
        layout.addLayout(btns)

    def _toggle_custom_edit(self) -> None:
        self.custom_edit.setEnabled(self.custom_radio.isChecked())

    def _browse_custom(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select patchbay executable", "", "All Files (*)")
        if file_path:
            self.custom_edit.setText(file_path)

    def _save(self) -> None:
        selected_app: str | None = None
        for k, rb in self.radio_buttons.items():
            if rb.isChecked():
                selected_app = k
                break
        if self.custom_radio.isChecked():
            selected_app = "custom"

        if not selected_app:
            QMessageBox.warning(self, "No selection", "Select a patchbay application or custom.")
            return

        custom_path = self.custom_edit.text().strip() if selected_app == "custom" else ""
        if selected_app == "custom" and not custom_path:
            QMessageBox.warning(self, "Invalid path", "Custom path cannot be empty.")
            return

        if not self.config.has_section("Patchbay"):
            self.config.add_section("Patchbay")

        self.config.set("Patchbay", "selected_app", selected_app)
        self.config.set("Patchbay", "custom_path", custom_path)

        self.store.save(self.config)
        self.accept()
