"""
Alpha-Beta Pruning (Negamax) — dùng cho cấp 3 và cấp 4.
Cấp 3 (depth=3): Alpha-Beta thuần.
Cấp 4 (depth=4): Alpha-Beta + Quiescence Search + Killer/History.
"""
from __future__ import annotations

import chess

from src.core.constants import INF, CHECKMATE, QDEPTH_MAX
from src.ai.evaluator import evaluate
from src.ai.move_ordering import KillerTable, HistoryTable, order_moves


# ── Quiescence Search ─────────────────────────────────────────────────────────
def _quiescence(
    board:   chess.Board,
    alpha:   int,
    beta:    int,
    qdepth:  int,
) -> int:
    """
    Chỉ duyệt các nước ăn quân để ổn định điểm số.
    Tránh Horizon Effect: không đánh giá giữa chừng chuỗi trao đổi quân.
    """
    # stand_pat: điểm hiện tại theo góc nhìn bên đang đi
    turn_factor = 1 if board.turn == chess.WHITE else -1
    stand_pat   = evaluate(board) * turn_factor

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat

    if qdepth <= 0:
        return alpha

    captures = [m for m in board.legal_moves if board.is_capture(m)]
    captures = order_moves(board, captures)

    for move in captures:
        board.push(move)
        score = -_quiescence(board, -beta, -alpha, qdepth - 1)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


# ── Negamax Alpha-Beta ────────────────────────────────────────────────────────
def _negamax(
    board:    chess.Board,
    depth:    int,
    alpha:    int,
    beta:     int,
    killers:  KillerTable,
    history:  HistoryTable,
    use_q:    bool,
    pv_move:  chess.Move | None = None,
) -> int:
    if board.is_game_over():
        if board.is_checkmate():
            # Bên đang có lượt đi bị chiếu bí → thua → âm vô cực
            return -(CHECKMATE - 50)   # -50 để AI ưu tiên checkmate nhanh hơn
        return 0  # hòa

    if depth == 0:
        if use_q:
            return _quiescence(board, alpha, beta, QDEPTH_MAX)
        turn_factor = 1 if board.turn == chess.WHITE else -1
        return evaluate(board) * turn_factor

    legal   = list(board.legal_moves)
    ordered = order_moves(board, legal, depth, killers, history, pv_move)

    best = -INF
    for move in ordered:
        board.push(move)
        score = -_negamax(board, depth - 1, -beta, -alpha,
                          killers, history, use_q)
        board.pop()

        if score > best:
            best = score

        if score >= beta:
            # Beta cutoff: cập nhật Killer và History
            if not board.is_capture(move):
                killers.store(move, depth)
                history.update(move, depth)
            return beta

        if score > alpha:
            alpha = score

    return best


# ── Entry Point ───────────────────────────────────────────────────────────────
def find_move_alphabeta(
    board:    chess.Board,
    depth:    int,
    use_q:    bool = False,
    killers:  KillerTable  | None = None,
    history:  HistoryTable | None = None,
    pv_move:  chess.Move   | None = None,
) -> chess.Move | None:
    """
    Tìm nước đi tốt nhất bằng Alpha-Beta Pruning (Negamax).

    Args:
        depth:   Độ sâu tìm kiếm.
        use_q:   True → bật Quiescence Search ở lá (cấp 4).
        killers: Dùng chung với IDDFS nếu có.
        history: Dùng chung với IDDFS nếu có.
        pv_move: Nước PV từ IDDFS iteration trước.
    """
    legal = list(board.legal_moves)
    if not legal:
        return None

    _killers = killers or KillerTable()
    _history = history or HistoryTable()

    best_move  = legal[0]
    best_score = -INF
    alpha      = -INF
    beta       =  INF

    ordered = order_moves(board, legal, depth, _killers, _history, pv_move)

    for move in ordered:
        board.push(move)
        score = -_negamax(board, depth - 1, -beta, -alpha,
                          _killers, _history, use_q)
        board.pop()

        if score > best_score:
            best_score = score
            best_move  = move

        if score > alpha:
            alpha = score

    return best_move

