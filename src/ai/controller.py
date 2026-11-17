"""
AIController: Cổng thống nhất chọn thuật toán AI theo cấp độ.

Level 1 → Minimax depth 1 (40% ngẫu nhiên)
Level 2 → Minimax depth 2
Level 3 → Alpha-Beta depth 3
Level 4 → Alpha-Beta depth 4 + Quiescence Search
Level 5 → Iterative Deepening + NegaScout (time-limited)
"""
from __future__ import annotations

import chess

from src.core.constants import AiLevel
from src.ai.minimax     import find_move_minimax
from src.ai.alpha_beta  import find_move_alphabeta
from src.ai.negascout   import find_move_iddfs


def get_best_move(board: chess.Board, level: int) -> chess.Move | None:
    """
    Trả về nước đi tốt nhất cho bên đang có lượt đi.

    Args:
        board: Trạng thái bàn cờ hiện tại (sẽ được sao chép trước khi tìm kiếm).
        level: Cấp độ AI (1–5), xem AiLevel.
    """
    # Worker sẽ truyền board.copy() vào đây, nhưng để an toàn tuyệt đối
    working_board = board.copy()

    if level == AiLevel.BEGINNER:
        return find_move_minimax(working_board, level=1)

    if level == AiLevel.EASY:
        return find_move_minimax(working_board, level=2)

    if level == AiLevel.MEDIUM:
        return find_move_alphabeta(
            working_board,
            depth=AiLevel.DEPTH[AiLevel.MEDIUM],
            use_q=False,
        )

    if level == AiLevel.HARD:
        return find_move_alphabeta(
            working_board,
            depth=AiLevel.DEPTH[AiLevel.HARD],
            use_q=True,
        )

    if level == AiLevel.EXPERT:
        return find_move_iddfs(
            working_board,
            max_depth=AiLevel.DEPTH[AiLevel.EXPERT],
            time_limit=AiLevel.TIME_LIMIT[AiLevel.EXPERT],
        )

    # Fallback an toàn
    return find_move_alphabeta(working_board, depth=3)

