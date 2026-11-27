"""
MainWindow: Cửa sổ chính của ứng dụng Chess Desktop.
Điều phối BoardWidget, InfoPanel, GameMenuDialog, AIWorker và GameState.
"""
from __future__ import annotations

import chess
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QWidget,
)

from src.core.constants import AiLevel, EndgameLevel, GameMode
from src.core.game_state import GameState
from src.core.puzzles import find_mate_in_1_move, get_puzzles_by_level
from src.ai.worker import AIWorker

from .board_widget import BoardWidget
from .info_panel import InfoPanel
from .game_menu import GameMenuDialog


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("♟ Chess - VKU DACS4")
        self.setMinimumSize(760, 560)

        self._state    = GameState()
        self._worker:  AIWorker | None = None   # thread AI hiện tại

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

        self.board_widget = BoardWidget()
        layout.addWidget(self.board_widget, stretch=1)

        self.info_panel = InfoPanel()
        self.info_panel.setStyleSheet("""
            QWidget {
                background-color: #16213e;
                color: #e0e0e0;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.info_panel)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

        # Kết nối signal
        self.board_widget.move_made.connect(self._on_human_move)
        self.info_panel.new_game_clicked.connect(self._show_game_menu)
        self.info_panel.flip_clicked.connect(self.board_widget.flip)
        self.info_panel.undo_clicked.connect(self._undo)
        self.info_panel.resign_clicked.connect(self._resign)
        self.info_panel.hint_clicked.connect(self._on_endgame_hint)
        self.info_panel.next_puzzle_clicked.connect(self._next_endgame_puzzle)

        # Khởi tạo trạng thái ban đầu
        self.info_panel.set_pvp_mode()
        self.info_panel.update_state(self.board_widget.board)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self._undo)
        QShortcut(QKeySequence("F"),      self).activated.connect(self.board_widget.flip)
        QShortcut(QKeySequence("N"),      self).activated.connect(self._show_game_menu)

    def _update_status_bar(self) -> None:
        self.status_bar.showMessage(
            "Kéo-thả quân cờ để di chuyển  |  "
            "Phím tắt: Ctrl+Z = Hoàn tác,  F = Lật bàn,  N = Ván mới"
        )

    # ── Game Menu ─────────────────────────────────────────────────────────────
    def _show_game_menu(self) -> None:
        """Hiện dialog chọn chế độ chơi."""
        dlg = GameMenuDialog(self)
        if dlg.exec() != GameMenuDialog.Accepted:
            return

        self._cancel_worker()   # Dừng AI thread cũ nếu đang chạy

        # Áp dụng cấu hình mới vào GameState
        self._state.set_mode(
            mode          = dlg.selected_mode,
            ai_level      = dlg.selected_level,
            human_color   = dlg.human_color,
            endgame_level = dlg.selected_endgame_level,
        )

        # Reset bàn cờ và UI
        self.board_widget.reset()
        self.info_panel.clear_history()

        if self._state.is_pve:
            level_name = AiLevel.LABELS.get(self._state.ai_level, "")
            self.info_panel.set_pve_mode(level_name)
            # Nếu người chơi cầm Đen → AI đi trước
            if self._state.human_color == chess.BLACK:
                self.board_widget.flip()
                self._trigger_ai()
        elif self._state.is_endgame:
            self._load_current_puzzle()
        else:
            self.info_panel.set_pvp_mode()

        self.info_panel.update_state(self.board_widget.board)

    # ── Người chơi đi ────────────────────────────────────────────────────────
    def _on_human_move(self, move: chess.Move) -> None:
        """Nhận signal từ BoardWidget sau khi người chơi kéo thả xong."""
        board = self.board_widget.board

        # Lấy SAN (board đã push rồi)
        san_str = self._get_san(board, move)
        is_white = (board.turn == chess.BLACK)   # sau push turn đã đổi
        self.info_panel.add_move(san_str, board.fullmove_number, is_white)
        self.info_panel.update_state(board)

        if self._state.is_endgame:
            self._handle_endgame_move(board)
            return

        if board.is_game_over():
            self._show_game_over(board)
            return

        # Nếu PvE và đến lượt AI → kích hoạt worker
        if self._state.is_ai_turn(board):
            self._trigger_ai()

    # ── Thế cờ tàn (Mate in 1) ────────────────────────────────────────────────
    def _load_current_puzzle(self) -> None:
        """Nạp thế cờ tàn hiện tại lên bàn cờ."""
        puzzles = get_puzzles_by_level(self._state.endgame_level)
        if not puzzles:
            return
        idx = self._state.puzzle_index % len(puzzles)
        self._state.puzzle_index = idx
        puzzle = puzzles[idx]

        # Xoay bàn cờ theo phe đi trước
        temp_board = chess.Board(puzzle.fen)
        flip = (temp_board.turn == chess.BLACK)

        self.board_widget.setEnabled(True)
        self.board_widget.load_fen(puzzle.fen, flip=flip)
        self.info_panel.clear_history()

        level_name = EndgameLevel.LABELS.get(self._state.endgame_level, "")
        self.info_panel.set_endgame_mode(
            level_name=level_name,
            puzzle_title=puzzle.title,
            current=idx + 1,
            total=len(puzzles),
        )
        self.info_panel.update_state(self.board_widget.board)

    def _handle_endgame_move(self, board: chess.Board) -> None:
        """Kiểm tra nước đi trong chế độ Thế cờ tàn (buộc phải chiếu hết trong 1 nước)."""
        puzzles = get_puzzles_by_level(self._state.endgame_level)
        puzzle = puzzles[self._state.puzzle_index]

        if board.is_checkmate():
            self._state.solved_puzzles.add(puzzle.id)
            self.info_panel.set_endgame_status(
                f"✅ Chính xác! Chiếu hết!\n{puzzle.title}",
                is_success=True,
            )
            box = QMessageBox(self)
            box.setWindowTitle("Chúc mừng!")
            box.setText(f"✅ Chiếu hết chính xác!\nThế cờ: {puzzle.title}")
            btn_next = box.addButton("Bài tiếp theo", QMessageBox.AcceptRole)
            box.addButton("Ở lại", QMessageBox.RejectRole)
            box.exec()
            if box.clickedButton() == btn_next:
                self._next_endgame_puzzle()
        else:
            self._state.puzzle_attempts += 1
            self.board_widget.setEnabled(False)
            self.info_panel.set_endgame_status(
                "❌ Chưa chiếu hết trong 1 nước! Đang hoàn tác để thử lại...",
                is_error=True,
            )
            QTimer.singleShot(550, self._revert_endgame_move)

    def _revert_endgame_move(self) -> None:
        """Trả lại vị trí ban đầu của thế cờ khi người chơi đi sai."""
        if not self._state.is_endgame:
            return
        self._load_current_puzzle()
        puzzles = get_puzzles_by_level(self._state.endgame_level)
        puzzle = puzzles[self._state.puzzle_index]
        self.info_panel.set_endgame_status(
            f"❌ Nước vừa rồi chưa chiếu hết!\n🎯 {puzzle.title}",
            is_error=True,
        )

    def _on_endgame_hint(self) -> None:
        """Hiển thị gợi ý quân cờ cần đi và mô tả đòn đánh."""
        if not self._state.is_endgame:
            return
        puzzles = get_puzzles_by_level(self._state.endgame_level)
        puzzle = puzzles[self._state.puzzle_index]
        mate_move = find_mate_in_1_move(self.board_widget.board.copy())
        if mate_move:
            self.board_widget.show_hint(mate_move.from_square)
        self.info_panel.set_endgame_status(f"💡 Gợi ý: {puzzle.hint}")

    def _next_endgame_puzzle(self) -> None:
        """Chuyển sang thế cờ tiếp theo trong cấp độ."""
        if not self._state.is_endgame:
            return
        puzzles = get_puzzles_by_level(self._state.endgame_level)
        self._state.puzzle_index = (self._state.puzzle_index + 1) % len(puzzles)
        self._load_current_puzzle()

    # ── AI Worker ─────────────────────────────────────────────────────────────
    def _trigger_ai(self) -> None:
        """Khởi động AIWorker trong thread riêng."""
        self._cancel_worker()

        self.board_widget.setEnabled(False)
        self.info_panel.set_board_locked(True)

        self._worker = AIWorker(
            board = self.board_widget.board,
            level = self._state.ai_level,
            parent= self,
        )
        self._worker.status_update.connect(self.info_panel.set_ai_status)
        self._worker.move_ready.connect(self._on_ai_move)
        self._worker.thinking_finished.connect(self._on_ai_done)
        self._worker.start()

    def _on_ai_move(self, move: chess.Move) -> None:
        """Nhận nước đi từ AI worker và áp dụng lên bàn cờ."""
        board = self.board_widget.board
        if move not in board.legal_moves:
            return

        # Lấy SAN trước khi push
        san_str = board.san(move)

        self.board_widget.apply_move(move)   # BoardWidget push + repaint
        board = self.board_widget.board

        is_white = (board.turn == chess.BLACK)
        self.info_panel.add_move(san_str, board.fullmove_number, is_white)
        self.info_panel.update_state(board)

        if board.is_game_over():
            self._show_game_over(board)

    def _on_ai_done(self) -> None:
        """Gọi khi AI thread kết thúc — mở khoá bàn cờ."""
        self.board_widget.setEnabled(True)
        self.info_panel.set_board_locked(False)
        self._worker = None

    def _cancel_worker(self) -> None:
        """Dừng AI worker hiện tại (nếu có)."""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(500)
        self._worker = None

    # ── Undo ─────────────────────────────────────────────────────────────────
    def _undo(self) -> None:
        """
        PvP: Lùi 1 nước.
        PvE: Lùi 2 nước (nước máy + nước người) để trả lại đúng lượt.
        """
        if self._state.is_endgame:
            self._load_current_puzzle()
            return

        if self._state.is_pve and self._worker and self._worker.isRunning():
            return   # Không undo khi AI đang tính

        board = self.board_widget.board
        steps = 2 if self._state.is_pve else 1

        for _ in range(steps):
            if not board.move_stack:
                break
            board.pop()
            self.info_panel.pop_last_move()

        self.board_widget._selected   = None
        self.board_widget._legal_dsts = set()
        self.board_widget._last_move  = board.peek() if board.move_stack else None
        self.board_widget.update()
        self.info_panel.update_state(board)

        if self._state.is_pve:
            self.info_panel.set_ai_status("🤖 Máy sẵn sàng")

    # ── Resign ────────────────────────────────────────────────────────────────
    def _resign(self) -> None:
        reply = QMessageBox.question(
            self, "Đầu hàng",
            "Bạn chắc chắn muốn đầu hàng?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._cancel_worker()
        human  = self._state.human_color
        winner = "⬛ Đen (Máy)" if human == chess.WHITE else "⬜ Trắng (Máy)"
        box = QMessageBox(self)
        box.setWindowTitle("Đầu hàng")
        box.setText(f"🏳 Bạn đã đầu hàng.\n{winner} thắng!")
        box.setStandardButtons(QMessageBox.Ok)
        box.exec()

    # ── Game Over ─────────────────────────────────────────────────────────────
    def _show_game_over(self, board: chess.Board) -> None:
        self._cancel_worker()
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
            msg = f"Kết quả: {board.result()}"

        box = QMessageBox(self)
        box.setWindowTitle("Kết thúc ván đấu")
        box.setText(msg)
        box.setStandardButtons(QMessageBox.Ok)
        box.button(QMessageBox.Ok).setText("Đóng")
        box.exec()

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _get_san(board: chess.Board, move: chess.Move) -> str:
        """Lấy SAN an toàn (board đã push rồi)."""
        try:
            tmp = board.copy()
            tmp.pop()
            return tmp.san(move)
        except Exception:
            return move.uci()

    def closeEvent(self, event) -> None:
        self._cancel_worker()
        super().closeEvent(event)
