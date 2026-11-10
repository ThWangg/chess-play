"""
Panel thông tin & điều khiển bên phải bàn cờ:
- Hiển thị lượt đi (Trắng / Đen)
- Trạng thái ván đấu (Chiếu, Chiếu bí, Hòa, v.v.)
- Lịch sử nước đi (SAN notation)
- Nút: New Game, Flip Board, Undo
"""
from __future__ import annotations

import chess
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class InfoPanel(QWidget):
    """Panel thông tin bên phải bàn cờ."""

    new_game_clicked = Signal()
    flip_clicked = Signal()
    undo_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self._move_history: list[str] = []  # danh sách SAN từng nước
        self._full_moves: list[str] = []    # dạng "1. e4 e5" cho display
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(12, 12, 12, 12)

        # ── Tiêu đề ──────────────────────────────────────────────────────
        title = QLabel("♟ Cờ Vua")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        root.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setFrameShadow(QFrame.Sunken)
        root.addWidget(sep)

        # ── Lượt đi ──────────────────────────────────────────────────────
        self._turn_label = QLabel("Lượt: ⬜ Trắng")
        self._turn_label.setAlignment(Qt.AlignCenter)
        self._turn_label.setFont(QFont("Arial", 12))
        root.addWidget(self._turn_label)

        # ── Trạng thái ───────────────────────────────────────────────────
        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setFont(QFont("Arial", 11))
        self._status_label.setStyleSheet("color: #c0392b; font-weight: bold;")
        self._status_label.setWordWrap(True)
        root.addWidget(self._status_label)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine); sep2.setFrameShadow(QFrame.Sunken)
        root.addWidget(sep2)

        # ── Lịch sử nước đi ──────────────────────────────────────────────
        hist_label = QLabel("Lịch sử nước đi:")
        hist_label.setFont(QFont("Arial", 10, QFont.Bold))
        root.addWidget(hist_label)

        self._move_list = QListWidget()
        self._move_list.setAlternatingRowColors(True)
        self._move_list.setFocusPolicy(Qt.NoFocus)
        self._move_list.setStyleSheet("""
            QListWidget { font-family: 'Courier New'; font-size: 11px; }
            QListWidget::item:selected { background: #3498db; color: white; }
        """)
        self._move_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self._move_list)

        # ── Buttons ───────────────────────────────────────────────────────
        btn_style = """
            QPushButton {
                background-color: #2c3e50; color: white;
                border: none; border-radius: 6px;
                padding: 7px; font-size: 12px;
            }
            QPushButton:hover { background-color: #3d5a73; }
            QPushButton:pressed { background-color: #1a252f; }
        """
        btn_new = QPushButton("🔄 Ván mới")
        btn_new.setStyleSheet(btn_style)
        btn_new.clicked.connect(self.new_game_clicked)
        root.addWidget(btn_new)

        btn_row = QHBoxLayout()

        btn_flip = QPushButton("🔃 Lật bàn")
        btn_flip.setStyleSheet(btn_style)
        btn_flip.clicked.connect(self.flip_clicked)
        btn_row.addWidget(btn_flip)

        btn_undo = QPushButton("↩ Hoàn tác")
        btn_undo.setStyleSheet(btn_style)
        btn_undo.clicked.connect(self.undo_clicked)
        btn_row.addWidget(btn_undo)

        root.addLayout(btn_row)

    # ── Public API ────────────────────────────────────────────────────────────
    def update_state(self, board: chess.Board) -> None:
        """Cập nhật toàn bộ panel sau mỗi nước đi."""
        # Lượt đi
        if not board.is_game_over():
            if board.turn == chess.WHITE:
                self._turn_label.setText("Lượt: ⬜ Trắng")
            else:
                self._turn_label.setText("Lượt: ⬛ Đen")
        # Trạng thái
        status = self._get_status(board)
        self._status_label.setText(status)

    def _get_status(self, board: chess.Board) -> str:
        if board.is_checkmate():
            winner = "⬜ Trắng" if board.turn == chess.BLACK else "⬛ Đen"
            return f"♚ Chiếu bí!\n{winner} thắng!"
        if board.is_stalemate():
            return "🤝 Hòa cờ (Stalemate)"
        if board.is_insufficient_material():
            return "🤝 Hòa cờ (Thiếu quân)"
        if board.is_seventyfive_moves():
            return "🤝 Hòa cờ (75 nước)"
        if board.is_fivefold_repetition():
            return "🤝 Hòa cờ (Lặp lại 5 lần)"
        if board.is_fifty_moves():
            return "🤝 Hòa cờ (50 nước)"
        if board.is_check():
            return "⚠️ Chiếu tướng!"
        return ""

    def add_move(self, san: str, fullmove: int, is_white: bool) -> None:
        """Thêm 1 nước đi vào danh sách lịch sử."""
        if is_white:
            # Nước trắng: tạo dòng mới "N. san"
            row_text = f"{fullmove}. {san}"
            self._move_list.addItem(row_text)
        else:
            # Nước đen: gắn vào dòng cuối
            count = self._move_list.count()
            if count > 0:
                current = self._move_list.item(count - 1).text()
                self._move_list.item(count - 1).setText(f"{current}  {san}")
            else:
                self._move_list.addItem(f"...  {san}")
        self._move_list.scrollToBottom()

    def clear_history(self) -> None:
        self._move_list.clear()

