"""
GameMenuDialog: Dialog chọn chế độ chơi trước khi bắt đầu ván mới.
Hiển thị khi bấm "Ván mới" hoặc lần đầu khởi động.
"""
from __future__ import annotations

import chess
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from src.core.constants import AiLevel, GameMode

_DIALOG_STYLE = """
QDialog {
    background-color: #1a1a2e;
    color: #e0e0e0;
}
QLabel {
    color: #e0e0e0;
    background: transparent;
}
QRadioButton {
    color: #e0e0e0;
    font-size: 13px;
    spacing: 8px;
    background: transparent;
}
QRadioButton::indicator { width: 16px; height: 16px; }
QComboBox {
    background-color: #2c3e50;
    color: #e0e0e0;
    border: 1px solid #3d5a73;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
    min-height: 28px;
}
QComboBox QAbstractItemView {
    background-color: #2c3e50;
    color: #e0e0e0;
    selection-background-color: #3498db;
}
QDialogButtonBox QPushButton {
    background-color: #2980b9;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    min-width: 90px;
}
QDialogButtonBox QPushButton:hover { background-color: #3498db; }
QDialogButtonBox QPushButton:pressed { background-color: #1a6a9a; }
"""


class GameMenuDialog(QDialog):
    """
    Dialog chọn:
      - Chế độ: PvP hoặc PvE
      - Cấp độ AI (ẩn khi PvP)
      - Phe người chơi (ẩn khi PvP)
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Bắt đầu ván mới")
        self.setModal(True)
        self.setMinimumWidth(360)
        self.setStyleSheet(_DIALOG_STYLE)
        self._setup_ui()

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setFrameShadow(QFrame.Sunken)
        f.setStyleSheet("background-color: #2c3e50;")
        return f

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(24, 20, 24, 20)

        # ── Tiêu đề ─────────────────────────────────────────────────────────
        title = QLabel("♟ Chọn Chế Độ Chơi")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 15, QFont.Bold))
        root.addWidget(title)
        root.addWidget(self._sep())

        # ── Chế độ chơi ─────────────────────────────────────────────────────
        mode_label = QLabel("Chế độ:")
        mode_label.setFont(QFont("Arial", 11, QFont.Bold))
        root.addWidget(mode_label)

        mode_row = QHBoxLayout()
        self._rb_pvp = QRadioButton("👥  Người vs Người")
        self._rb_pve = QRadioButton("🤖  Người vs Máy")
        self._rb_pvp.setChecked(True)
        self._mode_group = QButtonGroup(self)
        self._mode_group.addButton(self._rb_pvp)
        self._mode_group.addButton(self._rb_pve)
        mode_row.addWidget(self._rb_pvp)
        mode_row.addWidget(self._rb_pve)
        root.addLayout(mode_row)

        root.addWidget(self._sep())

        # ── Cấp độ AI ───────────────────────────────────────────────────────
        self._ai_section = QWidget()
        ai_layout = QVBoxLayout(self._ai_section)
        ai_layout.setContentsMargins(0, 0, 0, 0)
        ai_layout.setSpacing(8)

        level_label = QLabel("Cấp độ AI:")
        level_label.setFont(QFont("Arial", 11, QFont.Bold))
        ai_layout.addWidget(level_label)

        self._level_combo = QComboBox()
        for lvl, name in AiLevel.LABELS.items():
            self._level_combo.addItem(name, userData=lvl)
        self._level_combo.setCurrentIndex(2)   # Trung bình mặc định
        ai_layout.addWidget(self._level_combo)

        # ── Phe người chơi ──────────────────────────────────────────────────
        color_label = QLabel("Cầm quân:")
        color_label.setFont(QFont("Arial", 11, QFont.Bold))
        ai_layout.addWidget(color_label)

        color_row = QHBoxLayout()
        self._rb_white = QRadioButton("⬜  Trắng (đi trước)")
        self._rb_black = QRadioButton("⬛  Đen")
        self._rb_white.setChecked(True)
        self._color_group = QButtonGroup(self)
        self._color_group.addButton(self._rb_white)
        self._color_group.addButton(self._rb_black)
        color_row.addWidget(self._rb_white)
        color_row.addWidget(self._rb_black)
        ai_layout.addLayout(color_row)

        root.addWidget(self._ai_section)
        root.addWidget(self._sep())

        # ── Nút OK / Hủy ────────────────────────────────────────────────────
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("▶  Bắt đầu")
        btns.button(QDialogButtonBox.Cancel).setText("Hủy")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

        # Kết nối toggle hiển thị AI section
        self._rb_pvp.toggled.connect(self._on_mode_changed)
        self._on_mode_changed(True)   # init state

    def _on_mode_changed(self, _: bool) -> None:
        self._ai_section.setVisible(self._rb_pve.isChecked())
        self.adjustSize()

    # ── Getters kết quả ───────────────────────────────────────────────────────
    @property
    def selected_mode(self) -> str:
        return GameMode.PVE if self._rb_pve.isChecked() else GameMode.PVP

    @property
    def selected_level(self) -> int:
        return self._level_combo.currentData()

    @property
    def human_color(self) -> chess.Color:
        return chess.WHITE if self._rb_white.isChecked() else chess.BLACK

