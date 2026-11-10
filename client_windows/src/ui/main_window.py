"""
MainWindow: Cửa sổ chính của ứng dụng Chess Desktop.
Ghép BoardWidget + InfoPanel, xử lý logic điều khiển cấp cao.
"""
from __future__ import annotations

import chess
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QWidget,
)

from .board_widget import BoardWidget
from .info_panel import InfoPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("♟ Chess - VKU DACS4")
        self.setMinimumSize(720, 540)
        self._setup_ui()
        self._setup_shortcuts()

    # ── UI setup ──────────────────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QWidget#central { background-color: #1a1a2e; }
        """)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Bàn cờ
        self.board_widget = BoardWidget()
        layout.addWidget(self.board_widget, stretch=1)

        # Panel thông tin
        self.info_panel = InfoPanel()
        self.info_panel.setStyleSheet("""
            QWidget {
                background-color: #16213e;
                color: #e0e0e0;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.info_panel)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Kéo-thả quân cờ để di chuyển  |  Phím tắt: Ctrl+Z = Hoàn tác, F = Lật bàn, N = Ván mới")

        # Kết nối signal
        self.board_widget.move_made.connect(self._on_move_made)
        self.info_panel.new_game_clicked.connect(self._new_game)
        self.info_panel.flip_clicked.connect(self.board_widget.flip)
        self.info_panel.undo_clicked.connect(self._undo)

        # Trạng thái ban đầu
        self.info_panel.update_state(self.board_widget.board)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self._undo)
        QShortcut(QKeySequence("F"), self).activated.connect(self.board_widget.flip)
        QShortcut(QKeySequence("N"), self).activated.connect(self._new_game)

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _on_move_made(self, move: chess.Move) -> None:
        board = self.board_widget.board
        # Lấy SAN của nước vừa đi (đã push rồi nên pop để lấy SAN, rồi push lại)
        # python-chess lưu SAN trong stack khi push
        san = board.move_stack[-1] if board.move_stack else move
        # Lấy SAN an toàn
        try:
            # Lấy từ move_stack
            last_board = board.copy()
            last_board.pop()
            san_str = last_board.san(move)
        except Exception:
            san_str = move.uci()

        # Lượt đi TRƯỚC khi board đã cập nhật turn
        is_white_move = board.turn == chess.BLACK  # sau push, turn đã đổi
        full_move = board.fullmove_number

        self.info_panel.add_move(san_str, full_move, is_white=is_white_move)
        self.info_panel.update_state(board)

        # Kiểm tra kết thúc ván
        if board.is_game_over():
            self._show_game_over(board)

    def _show_game_over(self, board: chess.Board) -> None:
        result = board.result()
        outcome = board.outcome()
        if outcome:
            term = outcome.termination.name.replace("_", " ").title()
            if outcome.winner is chess.WHITE:
                msg = f"⬜ Trắng thắng!\n({term})"
            elif outcome.winner is chess.BLACK:
                msg = f"⬛ Đen thắng!\n({term})"
            else:
                msg = f"🤝 Hòa cờ!\n({term})"
        else:
            msg = f"Kết quả: {result}"

        box = QMessageBox(self)
        box.setWindowTitle("Kết thúc ván đấu")
        box.setText(msg)
        box.setStandardButtons(QMessageBox.Ok)
        box.button(QMessageBox.Ok).setText("Đóng")
        box.exec()

    def _new_game(self) -> None:
        reply = QMessageBox.question(
            self, "Ván mới",
            "Bắt đầu ván cờ mới?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            self.board_widget.reset()
            self.info_panel.clear_history()
            self.info_panel.update_state(self.board_widget.board)

    def _undo(self) -> None:
        board = self.board_widget.board
        if not board.move_stack:
            return
        board.pop()
        self.board_widget._selected = None
        self.board_widget._legal_dsts = set()
        self.board_widget._last_move = board.peek() if board.move_stack else None
        self.board_widget.update()
        # Xóa dòng cuối trong lịch sử
        count = self.info_panel._move_list.count()
        if count > 0:
            last_item = self.info_panel._move_list.item(count - 1)
            text = last_item.text()
            parts = text.rsplit("  ", 1)
            if len(parts) == 2 and not parts[0].endswith("."):
                # Có cả nước trắng và đen -> xóa nước đen
                last_item.setText(parts[0])
            else:
                # Chỉ có nước trắng -> xóa cả dòng
                self.info_panel._move_list.takeItem(count - 1)
        self.info_panel.update_state(board)

