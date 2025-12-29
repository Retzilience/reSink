# source/ui_main_window.py
from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app_meta import APP_NAME, REPO_URL, detect_version
from config_store import ConfigStore
from dialogs_create_sink import CreateVirtualSinkDialog
from dialogs_patchbay_settings import PatchbaySettingsDialog
from patchbay import launch_patchbay, resolve_patchbay_choice
from rehelp import HelpDialog
from reupdater import UpdateClient, project_from_repo
from resink_backend import ReSinkBackend, SinkInfo, destroy_sink_by_name, set_default_sink
from ui_help_content import help_html
from ui_rows import SinkRow, SinkRowModel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} - Virtual Sink Manager")
        self.resize(520, 680)

        self.backend = ReSinkBackend()
        self.store = ConfigStore()
        self.store.ensure_exists()
        # I record my executable path so other apps (like aSyphon) can locate this installed build.
        self.store.record_last_exe_path()

        self._project = project_from_repo(
            REPO_URL,
            version=detect_version(),
            name=APP_NAME,
            settings_org="Retzilience",
            settings_app=APP_NAME,
        )
        self._updater = UpdateClient(self, self._project)

        root = QWidget()
        outer = QVBoxLayout()
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(10)
        root.setLayout(outer)
        self.setCentralWidget(root)

        outer.addLayout(self._make_header())

        self.sinks_panel = self._make_panel("Sinks")
        self.sinks_list = self._make_sinks_list()
        self.sinks_panel_layout.addWidget(self.sinks_list, 1)
        outer.addWidget(self.sinks_panel, 1)

        outer.addLayout(self._make_footer_actions())

        self.refresh()

    def _open_help(self) -> None:
        dlg = HelpDialog(
            self,
            self._project,
            html=help_html(self._project.name or self._project.repo),
            updater=self._updater,
        )
        dlg.exec()

    def _make_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(10)

        title = QLabel(APP_NAME)
        title.setObjectName("Title")
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        backend = QLabel(self.backend.server_label())
        backend.setObjectName("Subtle")
        backend.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        backend.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        help_btn = QPushButton("Help / About")
        help_btn.clicked.connect(self._open_help)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)

        header.addWidget(title, 2)
        header.addWidget(backend, 3)
        header.addWidget(help_btn, 0)
        header.addWidget(refresh_btn, 0)
        return header

    def _make_panel(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        frame.setLayout(layout)

        top = QHBoxLayout()
        top.setSpacing(10)

        t = QLabel(title)
        f = QFont()
        f.setPointSize(12)
        f.setWeight(QFont.DemiBold)
        t.setFont(f)

        self._panel_right = QLabel("")
        self._panel_right.setObjectName("Subtle")
        self._panel_right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        top.addWidget(t)
        top.addStretch(1)
        top.addWidget(self._panel_right)
        layout.addLayout(top)

        self.sinks_panel_layout = layout
        return frame

    def _make_sinks_list(self) -> QScrollArea:
        container = QWidget()
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)
        container.setLayout(v)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(container)

        scroll.setAlignment(Qt.AlignTop)

        scroll._container = container  # type: ignore[attr-defined]
        scroll._layout = v  # type: ignore[attr-defined]
        return scroll

    def _sinks_layout(self) -> QVBoxLayout:
        return self.sinks_list._layout  # type: ignore[attr-defined]

    def _clear_layout(self, lay: QVBoxLayout) -> None:
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _make_footer_actions(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        self.create_btn = QPushButton("Create New Virtual Sink")
        self.create_btn.setObjectName("Primary")
        self.create_btn.clicked.connect(self._create_sink)

        self.destroy_btn = QPushButton("Destroy Selected Sinks")
        self.destroy_btn.setObjectName("Danger")
        self.destroy_btn.clicked.connect(self._destroy_selected)

        self.default_btn = QPushButton("Make Default")
        self.default_btn.setObjectName("Primary")
        self.default_btn.clicked.connect(self._make_default)

        self.open_patch_btn = QPushButton("Open Patchbay")
        self.open_patch_btn.clicked.connect(self._open_patchbay)

        cog_icon = QIcon.fromTheme("preferences-system")
        settings_btn = QPushButton("⚙" if cog_icon.isNull() else "")
        settings_btn.setObjectName("Icon")
        if not cog_icon.isNull():
            settings_btn.setIcon(cog_icon)
        settings_btn.setFixedSize(38, 34)
        settings_btn.clicked.connect(self._patchbay_settings)

        row.addWidget(self.create_btn, 1)
        row.addWidget(self.destroy_btn, 1)
        row.addWidget(self.default_btn, 0)
        row.addWidget(self.open_patch_btn, 0)
        row.addWidget(settings_btn, 0)

        return row

    def _rows(self) -> List[SinkRow]:
        lay = self._sinks_layout()
        out: List[SinkRow] = []
        for i in range(lay.count()):
            w = lay.itemAt(i).widget()
            if isinstance(w, SinkRow):
                out.append(w)
        return out

    def _selected_virtual_sinks(self) -> List[SinkRowModel]:
        out: List[SinkRowModel] = []
        for r in self._rows():
            m = r.model()
            if not m:
                continue
            if m.is_virtual and r.is_selected():
                out.append(m)
        return out

    def _update_action_states(self) -> None:
        sel = self._selected_virtual_sinks()
        n = len(sel)

        total_rows = len(self._rows())
        self._panel_right.setText(f"{total_rows} items • {n} selected")

        self.destroy_btn.setEnabled(n > 0)
        self.default_btn.setEnabled(n == 1)

    def _rebuild_sink_rows(self, sinks: List[SinkInfo]) -> None:
        lay = self._sinks_layout()
        self._clear_layout(lay)

        for s in sinks:
            row = SinkRow()
            row.set_model(
                SinkRowModel(
                    name=s.name,
                    description=s.description,
                    is_virtual=s.is_virtual,
                    is_default=s.is_default,
                )
            )
            row.selection_changed.connect(self._update_action_states)
            lay.addWidget(row)

        self._update_action_states()

    def refresh(self) -> None:
        try:
            sinks = self.backend.list_sinks()
            self._rebuild_sink_rows(sinks)
        except Exception as e:
            QMessageBox.critical(self, "Backend error", str(e))

    def _create_sink(self) -> None:
        dlg = CreateVirtualSinkDialog(self)
        if dlg.exec():
            self.refresh()

    def _destroy_selected(self) -> None:
        sel = self._selected_virtual_sinks()
        if not sel:
            QMessageBox.information(self, "Destroy", "No virtual sinks selected.")
            return

        names = "\n".join(f"• {m.description}  [{m.name}]" for m in sel)
        ok = QMessageBox.question(
            self,
            "Destroy selected",
            f"This will destroy {len(sel)} virtual sink(s):\n\n{names}\n\nContinue?",
        )
        if ok != QMessageBox.StandardButton.Yes:
            return

        errors: List[str] = []
        for m in sel:
            try:
                destroy_sink_by_name(m.name)
            except Exception as e:
                errors.append(f"{m.name}: {e}")

        self.refresh()
        if errors:
            QMessageBox.critical(self, "Destroy issues", "\n".join(errors))

    def _make_default(self) -> None:
        sel = self._selected_virtual_sinks()
        if not sel:
            QMessageBox.information(self, "Make default", "Select one virtual sink to set as default.")
            return
        if len(sel) != 1:
            QMessageBox.warning(self, "Make default", "Select exactly one virtual sink.")
            return

        m = sel[0]
        try:
            set_default_sink(m.name)
        except Exception as e:
            QMessageBox.critical(self, "Make default", str(e))
            return

        self.refresh()

    def _patchbay_settings(self) -> None:
        dlg = PatchbaySettingsDialog(self.store, self)
        dlg.exec()

    def _open_patchbay(self) -> None:
        choice = resolve_patchbay_choice(self.store)
        if choice is None:
            QMessageBox.information(
                self,
                "Patchbay",
                "No patchbay is configured yet. Configure one in Patchbay settings.",
            )
            self._patchbay_settings()
            return

        launch_patchbay(choice, self)
