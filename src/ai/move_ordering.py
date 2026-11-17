"""
Move Ordering: Sắp xếp nước đi để tối đa hóa hiệu quả cắt tỉa Alpha-Beta.

Thứ tự ưu tiên (điểm cao = duyệt trước):
  1. Nước ăn quân (MVV-LVA: victim value cao - attacker value thấp)
  2. Phong cấp tốt thành Hậu
  3. Killer Moves (nước không ăn quân đã gây Beta cutoff)
  4. History Heuristic (tích lũy số lần gây cutoff)
  5. Nước thường
"""
from __future__ import annotations

import chess
from src.core.constants import PIECE_VALUES, KILLER_SLOTS


# ── MVV-LVA Score ─────────────────────────────────────────────────────────────
def _mvv_lva(board: chess.Board, move: chess.Move) -> int:
    """Most Valuable Victim – Least Valuable Attacker."""
    if not board.is_capture(move):
        return 0
    victim_sq = move.to_square
    # En passant: quân bị ăn không ở to_square
    if board.is_en_passant(move):
        return 10_000 + PIECE_VALUES[chess.PAWN] * 10 - PIECE_VALUES[chess.PAWN]

    victim   = board.piece_type_at(victim_sq) or chess.PAWN
    attacker = board.piece_type_at(move.from_square) or chess.PAWN
    return 10_000 + PIECE_VALUES[victim] * 10 - PIECE_VALUES[attacker]


# ── KillerTable ───────────────────────────────────────────────────────────────
class KillerTable:
    """
    Lưu tối đa KILLER_SLOTS nước đi không bắt quân gây Beta cutoff
    cho mỗi độ sâu (depth).
    """
    def __init__(self, max_depth: int = 32) -> None:
        # killers[depth] = [move1, move2, ...]
        self._table: list[list[chess.Move | None]] = [
            [None] * KILLER_SLOTS for _ in range(max_depth)
        ]

    def store(self, move: chess.Move, depth: int) -> None:
        if depth >= len(self._table):
            return
        slot = self._table[depth]
        if move not in slot:
            # Dịch sang phải, lưu move vào slot[0]
            slot[1] = slot[0]
            slot[0] = move

    def is_killer(self, move: chess.Move, depth: int) -> bool:
        if depth >= len(self._table):
            return False
        return move in self._table[depth]

    def score(self, move: chess.Move, depth: int) -> int:
        if not self.is_killer(move, depth):
            return 0
        idx = self._table[depth].index(move)
        return 8_000 - idx * 100   # killer[0] = 8000, killer[1] = 7900


# ── HistoryTable ──────────────────────────────────────────────────────────────
class HistoryTable:
    """
    Tích lũy điểm cho mỗi cặp (from_sq, to_sq) khi nước đó gây Beta cutoff.
    Chuẩn hóa định kỳ để tránh overflow.
    """
    def __init__(self) -> None:
        # [from_sq][to_sq] → int score
        self._table: list[list[int]] = [[0] * 64 for _ in range(64)]

    def update(self, move: chess.Move, depth: int) -> None:
        self._table[move.from_square][move.to_square] += depth * depth

    def score(self, move: chess.Move) -> int:
        return self._table[move.from_square][move.to_square]

    def normalize(self) -> None:
        """Chia đôi mọi giá trị sau mỗi ván để tránh giá trị quá lớn."""
        for row in self._table:
            for i in range(64):
                row[i] >>= 1   # right shift = chia 2


# ── Hàm sắp xếp chính ────────────────────────────────────────────────────────
def order_moves(
    board:   chess.Board,
    moves:   list[chess.Move],
    depth:   int            = 0,
    killers: KillerTable  | None = None,
    history: HistoryTable | None = None,
    pv_move: chess.Move   | None = None,
) -> list[chess.Move]:
    """
    Trả về danh sách nước đi đã sắp xếp theo điểm ưu tiên giảm dần.

    Args:
        board:   Trạng thái bàn cờ hiện tại.
        moves:   Danh sách chess.Move cần sắp xếp.
        depth:   Độ sâu hiện tại (dùng tra Killer Table).
        killers: KillerTable dùng chung cho toàn cây tìm kiếm.
        history: HistoryTable dùng chung.
        pv_move: Nước đi tốt nhất từ lần lặp IDDFS trước (ưu tiên cao nhất).
    """
    def _score(move: chess.Move) -> int:
        # 0. PV move từ Iterative Deepening
        if pv_move and move == pv_move:
            return 200_000

        # 1. Nước ăn quân (MVV-LVA)
        if board.is_capture(move):
            return 100_000 + _mvv_lva(board, move)

        # 2. Phong cấp
        if move.promotion == chess.QUEEN:
            return 90_000
        if move.promotion:
            return 50_000

        # 3. Killer Moves
        if killers:
            k = killers.score(move, depth)
            if k:
                return k

        # 4. History Heuristic
        if history:
            return history.score(move)

        return 0

    return sorted(moves, key=_score, reverse=True)

