"""
GameState: Trạng thái trung tâm của một ván đấu.
Lưu: chế độ chơi, cấp độ AI, phe người chơi, lịch sử SAN.
MainWindow đọc/ghi object này thay vì lưu state rải rác.
"""
from __future__ import annotations

import chess
from .constants import GameMode, AiLevel


class GameState:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Khởi tạo / đặt lại một ván đấu mới."""
        self.mode: str        = GameMode.PVP
        self.ai_level: int    = AiLevel.MEDIUM
        # Phe người chơi trong chế độ PvE (chess.WHITE hoặc chess.BLACK)
        self.human_color: chess.Color = chess.WHITE
        # Lịch sử nước đi dạng SAN: [("e4", True), ("e5", False), ...]
        # Tuple: (san_string, is_white_move)
        self.move_history: list[tuple[str, bool]] = []
        self.is_game_over: bool = False

    # ── Helpers ───────────────────────────────────────────────────────────────
    @property
    def is_pve(self) -> bool:
        return self.mode == GameMode.PVE

    @property
    def ai_color(self) -> chess.Color:
        """Màu của AI (ngược với người chơi) trong chế độ PvE."""
        return not self.human_color

    def is_ai_turn(self, board: chess.Board) -> bool:
        """Kiểm tra có phải lượt của AI không (chỉ áp dụng PvE)."""
        return self.is_pve and board.turn == self.ai_color and not self.is_game_over

    def add_move(self, san: str, is_white: bool) -> None:
        self.move_history.append((san, is_white))

    def undo_move(self) -> None:
        if self.move_history:
            self.move_history.pop()

    def undo_two_moves(self) -> None:
        """Undo 2 nước (nước máy + nước người) trong chế độ PvE."""
        for _ in range(min(2, len(self.move_history))):
            self.move_history.pop()

    def set_mode(self, mode: str, ai_level: int = AiLevel.MEDIUM,
                 human_color: chess.Color = chess.WHITE) -> None:
        self.mode        = mode
        self.ai_level    = ai_level
        self.human_color = human_color
        self.move_history.clear()
        self.is_game_over = False

