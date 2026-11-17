"""
NegaScout + Iterative Deepening Depth-First Search (IDDFS) — dùng cho cấp 5.

NegaScout (Principal Variation Search):
  - Giả định nước đi đầu tiên (đã sắp xếp tốt) là nước PV tốt nhất.
  - Các nước còn lại tìm bằng cửa sổ hẹp [α, α+1] (null-window) nhanh hơn.
  - Nếu null-window thất bại (score > α) mới tìm lại với cửa sổ đầy đủ.

IDDFS:
  - Tăng depth từ 1 lên max_depth.
  - Dừng khi vượt time_limit (giây).
  - Luôn trả về nước tốt nhất từ lần lặp sâu nhất hoàn thành.
  - Nước PV từ lần trước được đưa lên đầu Move Ordering → giúp cắt tỉa nhiều hơn.
"""
from __future__ import annotations

import time
import chess

from src.core.constants import INF, CHECKMATE, QDEPTH_MAX
from src.ai.evaluator import evaluate
from src.ai.move_ordering import KillerTable, HistoryTable, order_moves


# ── Shared state cho IDDFS ────────────────────────────────────────────────────
class _SearchContext:
    def __init__(self, time_limit: float) -> None:
        self.deadline    = time.monotonic() + time_limit
        self.cancelled   = False
        self.killers     = KillerTable(max_depth=64)
        self.history     = HistoryTable()
        self.nodes       = 0

    def check_time(self) -> bool:
        """Trả về True nếu đã hết thời gian."""
        if self.nodes % 2048 == 0:  # Kiểm tra mỗi 2048 node để không gọi quá nhiều
            if time.monotonic() >= self.deadline:
                self.cancelled = True
        return self.cancelled


# ── Quiescence Search ─────────────────────────────────────────────────────────
def _quiescence(board: chess.Board, alpha: int, beta: int, qdepth: int) -> int:
    turn_factor = 1 if board.turn == chess.WHITE else -1
    stand_pat   = evaluate(board) * turn_factor

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat
    if qdepth <= 0:
        return alpha

    captures = [m for m in board.legal_moves if board.is_capture(m)]
    for move in order_moves(board, captures):
        board.push(move)
        score = -_quiescence(board, -beta, -alpha, qdepth - 1)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


# ── NegaScout (PVS) ───────────────────────────────────────────────────────────
def _negascout(
    board:   chess.Board,
    depth:   int,
    alpha:   int,
    beta:    int,
    ctx:     _SearchContext,
    pv_move: chess.Move | None = None,
) -> int:
    ctx.nodes += 1

    if ctx.check_time():
        return 0  # Giá trị bị bỏ qua khi cancelled

    if board.is_game_over():
        if board.is_checkmate():
            return -(CHECKMATE - depth)  # Trừ depth để ưu tiên checkmate nhanh hơn
        return 0

    if depth == 0:
        return _quiescence(board, alpha, beta, QDEPTH_MAX)

    legal   = list(board.legal_moves)
    ordered = order_moves(board, legal, depth, ctx.killers, ctx.history, pv_move)

    is_pv_node = True  # Nước đầu tiên luôn là PV node

    for move in ordered:
        board.push(move)

        if is_pv_node:
            # Tìm kiếm đầy đủ cho PV move
            score = -_negascout(board, depth - 1, -beta, -alpha, ctx)
        else:
            # Null-window search cho các nước còn lại
            score = -_negascout(board, depth - 1, -alpha - 1, -alpha, ctx)
            # Nếu thất bại (cải thiện alpha) → tìm lại với cửa sổ đầy đủ
            if alpha < score < beta:
                score = -_negascout(board, depth - 1, -beta, -score, ctx)

        board.pop()

        if ctx.cancelled:
            return 0

        if score >= beta:
            # Beta cutoff
            if not board.is_capture(move):
                ctx.killers.store(move, depth)
                ctx.history.update(move, depth)
            return beta

        if score > alpha:
            alpha      = score
            is_pv_node = False  # Các nước sau mới dùng null-window

    return alpha


# ── Iterative Deepening ───────────────────────────────────────────────────────
def find_move_iddfs(
    board:      chess.Board,
    max_depth:  int   = 10,
    time_limit: float = 3.0,
) -> chess.Move | None:
    """
    Iterative Deepening + NegaScout (cấp 5).

    Tăng depth từ 1 → max_depth. Dừng khi vượt time_limit.
    Luôn trả về nước tốt nhất từ lần lặp hoàn thành cuối cùng.
    """
    legal = list(board.legal_moves)
    if not legal:
        return None
    if len(legal) == 1:
        return legal[0]   # Chỉ có 1 nước đi hợp lệ

    ctx      = _SearchContext(time_limit)
    best_move: chess.Move = legal[0]
    pv_move:  chess.Move | None = None

    for depth in range(1, max_depth + 1):
        if ctx.cancelled:
            break

        depth_best_move  = best_move
        depth_best_score = -INF
        alpha            = -INF
        beta             =  INF

        ordered = order_moves(board, legal, depth,
                              ctx.killers, ctx.history, pv_move)

        for move in ordered:
            if ctx.cancelled:
                break
            board.push(move)
            score = -_negascout(board, depth - 1, -beta, -alpha, ctx, None)
            board.pop()

            if score > depth_best_score:
                depth_best_score = score
                depth_best_move  = move

            if score > alpha:
                alpha   = score
                pv_move = move   # Cập nhật PV move cho lần lặp sau

        # Chỉ cập nhật best_move nếu lần lặp hoàn chỉnh (không bị cancel giữa chừng)
        if not ctx.cancelled:
            best_move = depth_best_move

    ctx.history.normalize()
    return best_move

