"""
Panel thông tin & điều khiển bên phải bàn cờ:
- Lượt đi, trạng thái ván đấu
- Trạng thái AI (khi PvE)
- Lịch sử nước đi (SAN notation)
- Nút: Ván mới, Lật bàn, Hoàn tác, Đầu hàng
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

    new_game_clicked  = Signal()
    flip_clicked      = Signal()
    undo_clicked      = Signal()
    resign_clicked    = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self._setup_ui()

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setFrameShadow(QFrame.Sunken)
        return f

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(12, 12, 12, 12)

        # ── Tiêu đề ──────────────────────────────────────────────────────────
        title = QLabel("♟ Cờ Vua")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        root.addWidget(title)
        root.addWidget(self._sep())

        # ── Chế độ chơi (label) ──────────────────────────────────────────────
        self._mode_label = QLabel("Chế độ: Người vs Người")
        self._mode_label.setAlignment(Qt.AlignCenter)
        self._mode_label.setFont(QFont("Arial", 10))
        self._mode_label.setStyleSheet("color: #95a5a6;")
        root.addWidget(self._mode_label)

        # ── Lượt đi ──────────────────────────────────────────────────────────
        self._turn_label = QLabel("Lượt: ⬜ Trắng")
        self._turn_label.setAlignment(Qt.AlignCenter)
        self._turn_label.setFont(QFont("Arial", 12, QFont.Bold))
        root.addWidget(self._turn_label)

        # ── Trạng thái ván (chiếu, hòa...) ──────────────────────────────────
        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setFont(QFont("Arial", 11))
        self._status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self._status_label.setWordWrap(True)
        root.addWidget(self._status_label)

        # ── AI status (ẩn khi PvP) ───────────────────────────────────────────
        self._ai_label = QLabel("")
        self._ai_label.setAlignment(Qt.AlignCenter)
        self._ai_label.setFont(QFont("Arial", 10))
        self._ai_label.setStyleSheet(
            "color: #3498db; font-style: italic; padding: 4px;"
            "background: #0d1b2a; border-radius: 4px;"
        )
        self._ai_label.setWordWrap(True)
        self._ai_label.setVisible(False)
        root.addWidget(self._ai_label)

        root.addWidget(self._sep())

        # ── Lịch sử nước đi ──────────────────────────────────────────────────
        hist_label = QLabel("Lịch sử nước đi:")
        hist_label.setFont(QFont("Arial", 10, QFont.Bold))
        root.addWidget(hist_label)

        self._move_list = QListWidget()
        self._move_list.setAlternatingRowColors(True)
        self._move_list.setFocusPolicy(Qt.NoFocus)
        self._move_list.setStyleSheet("""
            QListWidget { font-family: 'Courier New'; font-size: 11px; }
            QListWidget::item:selected { background: #2980b9; color: white; }
        """)
        self._move_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self._move_list)

        # ── Buttons ───────────────────────────────────────────────────────────
        _BTN = """
            QPushButton {
                background-color: #2c3e50; color: white;
                border: none; border-radius: 6px;
                padding: 7px; font-size: 12px;
            }
            QPushButton:hover  { background-color: #3d5a73; }
            QPushButton:pressed{ background-color: #1a252f; }
            QPushButton:disabled { background-color: #1a252f; color: #555; }
        """
        _BTN_RED = """
            QPushButton {
                background-color: #922b21; color: white;
                border: none; border-radius: 6px;
                padding: 7px; font-size: 12px;
            }
            QPushButton:hover  { background-color: #c0392b; }
            QPushButton:pressed{ background-color: #6b1f1a; }
            QPushButton:disabled { background-color: #2c1a1a; color: #555; }
        """

        btn_new = QPushButton("🔄 Ván mới")
        btn_new.setStyleSheet(_BTN)
        btn_new.clicked.connect(self.new_game_clicked)
        root.addWidget(btn_new)

        btn_row = QHBoxLayout()

        btn_flip = QPushButton("🔃 Lật bàn")
        btn_flip.setStyleSheet(_BTN)
        btn_flip.clicked.connect(self.flip_clicked)
        btn_row.addWidget(btn_flip)

        self._btn_undo = QPushButton("↩ Hoàn tác")
        self._btn_undo.setStyleSheet(_BTN)
        self._btn_undo.clicked.connect(self.undo_clicked)
        btn_row.addWidget(self._btn_undo)

        root.addLayout(btn_row)

        self._btn_resign = QPushButton("🏳 Đầu hàng")
        self._btn_resign.setStyleSheet(_BTN_RED)
        self._btn_resign.clicked.connect(self.resign_clicked)
        self._btn_resign.setVisible(False)   # chỉ hiện khi PvE
        root.addWidget(self._btn_resign)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_pve_mode(self, level_name: str) -> None:
        """Gọi khi bắt đầu chế độ PvE."""
        self._mode_label.setText(f"🤖 Người vs Máy  |  {level_name}")
        self._ai_label.setVisible(True)
        self._btn_resign.setVisible(True)
        self.set_ai_status("🤖 Máy sẵn sàng")

    def set_pvp_mode(self) -> None:
        """Gọi khi bắt đầu chế độ PvP."""
        self._mode_label.setText("👥 Người vs Người")
        self._ai_label.setVisible(False)
        self._btn_resign.setVisible(False)

    def set_ai_status(self, text: str) -> None:
        """Cập nhật dòng trạng thái AI (đang suy nghĩ / đã đi / sẵn sàng)."""
        self._ai_label.setText(text)

    def set_board_locked(self, locked: bool) -> None:
        """Khoá / mở khoá các nút hoàn tác trong lúc AI đang tính."""
        self._btn_undo.setEnabled(not locked)

    def update_state(self, board: chess.Board) -> None:
        """Cập nhật toàn bộ panel sau mỗi nước đi."""
        if not board.is_game_over():
            sym = "⬜" if board.turn == chess.WHITE else "⬛"
            side = "Trắng" if board.turn == chess.WHITE else "Đen"
            self._turn_label.setText(f"Lượt: {sym} {side}")
        self._status_label.setText(self._get_status(board))

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
            self._move_list.addItem(f"{fullmove}. {san}")
        else:
            count = self._move_list.count()
            if count > 0:
                cur = self._move_list.item(count - 1).text()
                self._move_list.item(count - 1).setText(f"{cur}  {san}")
            else:
                self._move_list.addItem(f"...  {san}")
        self._move_list.scrollToBottom()

    def clear_history(self) -> None:
        self._move_list.clear()

    def pop_last_move(self) -> None:
        """Xoá nước đi cuối trong danh sách (dùng khi Undo)."""
        count = self._move_list.count()
        if count == 0:
            return
        last = self._move_list.item(count - 1)
        text = last.text()
        parts = text.rsplit("  ", 1)
        # Nếu dòng có cả nước Trắng lẫn nước Đen → chỉ xoá nước Đen
        if len(parts) == 2 and not parts[0].strip().endswith("."):
            last.setText(parts[0])
        else:
            self._move_list.takeItem(count - 1)
