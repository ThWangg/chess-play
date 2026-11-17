"""
AIWorker: QThread chạy ngầm thuật toán AI — không block GUI PySide6.

Signals:
  thinking_started()          → MainWindow khoá bàn cờ, hiện label "Đang suy nghĩ..."
  thinking_finished()         → MainWindow mở khoá bàn cờ
  move_ready(chess.Move)      → MainWindow nhận nước đi và thực hiện
  status_update(str)          → MainWindow hiện text trạng thái (cấp độ, thời gian...)
"""
from __future__ import annotations

import time
import chess
from PySide6.QtCore import QThread, Signal

from src.core.constants import AiLevel
from src.ai.controller  import get_best_move


class AIWorker(QThread):
    thinking_started  = Signal()
    thinking_finished = Signal()
    move_ready        = Signal(object)   # chess.Move
    status_update     = Signal(str)

    def __init__(
        self,
        board:  chess.Board,
        level:  int = AiLevel.MEDIUM,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._board      = board.copy()   # snapshot độc lập, tránh race condition
        self._level      = level
        self._cancelled  = False

    def cancel(self) -> None:
        """Gọi khi người chơi bấm New Game hoặc Undo trước khi AI đi xong."""
        self._cancelled = True

    def run(self) -> None:
        label = AiLevel.LABELS.get(self._level, f"Cấp {self._level}")
        self.status_update.emit(f"🤖 Máy đang suy nghĩ... ({label})")
        self.thinking_started.emit()

        t0   = time.monotonic()
        move = get_best_move(self._board, self._level)
        elapsed = time.monotonic() - t0

        if not self._cancelled and move is not None:
            self.status_update.emit(
                f"🤖 Máy đã đi: {self._board.san(move)}  ({elapsed:.2f}s)"
            )
            self.move_ready.emit(move)
        else:
            self.status_update.emit("🤖 Máy đã sẵn sàng")

        self.thinking_finished.emit()

