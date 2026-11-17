"""
Minimax thuần (không cắt tỉa) — dùng cho cấp 1 và cấp 2.
Cấp 1 (depth=1): Thêm 40% ngẫu nhiên để mô phỏng người mới.
Cấp 2 (depth=2): Minimax đầy đủ, nhìn trước 2 lượt.
"""
from __future__ import annotations

import random
import chess

from src.core.constants import INF, CHECKMATE
from src.ai.evaluator import evaluate
from src.ai.move_ordering import order_moves


def _minimax(board: chess.Board, depth: int, is_maximizing: bool) -> int:
    if board.is_game_over() or depth == 0:
        return evaluate(board)

    legal = list(board.legal_moves)
    # Sắp xếp nhẹ: ăn quân trước để tăng hiệu quả dù không cắt tỉa
    ordered = order_moves(board, legal)

    if is_maximizing:
        best = -INF
        for move in ordered:
            board.push(move)
            score = _minimax(board, depth - 1, False)
            board.pop()
            best = max(best, score)
        return best
    else:
        best = INF
        for move in ordered:
            board.push(move)
            score = _minimax(board, depth - 1, True)
            board.pop()
            best = min(best, score)
        return best


def find_move_minimax(board: chess.Board, level: int) -> chess.Move | None:
    """
    Tìm nước đi bằng Minimax thuần.
    level=1: depth 1 + 40% ngẫu nhiên.
    level=2: depth 2, luôn chọn nước tốt nhất.
    """
    legal = list(board.legal_moves)
    if not legal:
        return None

    depth = level  # level 1→depth 1, level 2→depth 2

    # Cấp 1: 40% cơ hội chọn ngẫu nhiên
    if level == 1 and random.random() < 0.40:
        return random.choice(legal)

    is_white = board.turn == chess.WHITE
    best_move  = legal[0]
    best_score = -INF if is_white else INF

    ordered = order_moves(board, legal)

    for move in ordered:
        board.push(move)
        score = _minimax(board, depth - 1, not is_white)
        board.pop()

        if is_white and score > best_score:
            best_score = score
            best_move  = move
        elif not is_white and score < best_score:
            best_score = score
            best_move  = move

    return best_move

