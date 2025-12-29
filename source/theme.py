from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(20, 20, 22))
    pal.setColor(QPalette.WindowText, QColor(230, 230, 230))
    pal.setColor(QPalette.Base, QColor(14, 14, 16))
    pal.setColor(QPalette.AlternateBase, QColor(26, 26, 28))
    pal.setColor(QPalette.Text, QColor(230, 230, 230))
    pal.setColor(QPalette.Button, QColor(34, 34, 38))
    pal.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    pal.setColor(QPalette.Highlight, QColor(80, 110, 170))
    pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    pal.setColor(QPalette.Disabled, QPalette.Text, QColor(140, 140, 140))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(140, 140, 140))
    pal.setColor(QPalette.Disabled, QPalette.WindowText, QColor(140, 140, 140))
    app.setPalette(pal)

    app.setStyleSheet(
        """
        QMainWindow { background: #141416; }

        QLabel#Title {
            font-size: 16px;
            font-weight: 700;
        }

        QLabel#Subtle {
            color: #aeb3bc;
        }

        QFrame#Panel {
            background: #1b1b1f;
            border: 1px solid #2a2a30;
            border-radius: 10px;
        }

        QWidget#RowCard {
            background: #1f1f24;
            border: 1px solid #2a2a30;
            border-radius: 10px;
        }

        QWidget#RowCard[kind="virtual"] {
            border: 1px solid #3b4f7a;
        }

        QWidget#RowCard[kind="physical"] {
            background: #1c1c20;
            border: 1px solid #2a2a30;
        }

        QWidget#RowCard[selected="true"] {
            background: #202533;
            border: 1px solid #506eaa;
        }

        QWidget#RowCard[default="true"] QLabel#SinkTitle {
            color: #d6e2ff;
        }

        QLabel#SinkTitle {
            font-size: 13px;
            font-weight: 700;
        }

        QLabel#SinkName {
            color: #aeb3bc;
            font-size: 11px;
        }

        QLabel#KindPill {
            padding: 3px 10px;
            border-radius: 10px;
            font-weight: 700;
            letter-spacing: 0.5px;
            font-size: 10px;
        }

        QLabel#KindPill[kind="virtual"] {
            background: #23314a;
            border: 1px solid #3b4f7a;
            color: #d6e2ff;
        }

        QLabel#KindPill[kind="physical"] {
            background: #2a2a30;
            border: 1px solid #3a3a42;
            color: #d6d6d6;
        }

        QLabel#SelectBar {
            padding: 6px 10px;
            border-radius: 9px;
            font-weight: 700;
        }

        QLabel#SelectBar[sel="false"] {
            background: #2a2a30;
            border: 1px solid #3a3a42;
            color: #d6d6d6;
        }

        /* I use an amber/yellow selected state (your “pending” palette), but the text is still “Selected”. */
        QLabel#SelectBar[sel="true"] {
            background: #3a3424;
            border: 1px solid #7a6231;
            color: #f3e6c8;
        }

        QLineEdit, QSpinBox, QTextEdit {
            padding: 6px 10px;
            border-radius: 8px;
            border: 1px solid #2a2a30;
            background: #121216;
        }

        QPushButton {
            padding: 6px 10px;
            border-radius: 10px;
            border: 1px solid #2a2a30;
            background: #232329;
        }
        QPushButton:hover { background: #2a2a33; }

        QPushButton:disabled {
            color: #7c7c85;
            background: #1b1b1f;
            border: 1px solid #2a2a30;
        }

        /* I only show “Primary” styling while enabled. */
        QPushButton#Primary:enabled {
            background: #2c3a5a;
            border: 1px solid #3b4f7a;
        }
        QPushButton#Primary:enabled:hover { background: #34456c; }

        /* I only show “Danger” styling while enabled. */
        QPushButton#Danger:enabled {
            background: #3a2424;
            border: 1px solid #7a3131;
        }
        QPushButton#Danger:enabled:hover { background: #442b2b; }

        QPushButton#Icon {
            padding: 0px;
            border-radius: 10px;
            border: 1px solid #2a2a30;
            background: #232329;
        }
        QPushButton#Icon:hover { background: #2a2a33; }
        """
    )
