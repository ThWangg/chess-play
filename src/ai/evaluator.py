"""
Evaluator: Hàm lượng giá thế cờ tổng hợp.
Điểm dương = Trắng ưu thế, điểm âm = Đen ưu thế.

Thành phần:
  A. Material Score     – Giá trị chất lượng quân
  B. Piece-Square Table – Điểm vị trí từng quân
  C. King Safety        – An toàn của vua
  D. Pawn Structure     – Tốt đôi / tốt lẻ / tốt thông
  E. Mobility           – Số nước đi hợp lệ
"""
from __future__ import annotations

import chess
from src.core.constants import PIECE_VALUES, CHECKMATE, DRAW

# ── Piece-Square Tables (PST) ──────────────────────────────────────────────────
# Index 0 = A1 (góc dưới trái Trắng), index 63 = H8 (góc trên phải Trắng)
# Trắng dùng thẳng; Đen dùng chess.square_mirror(sq) để lật theo trục ngang

_PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

_KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

_BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

_ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]

_QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

# Vua: an toàn ở giai đoạn trung cuộc (ưu tiên nhập thành, ẩn sau tốt)
_KING_MID_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

# Vua: giai đoạn tàn cuộc (vua nên tiến ra giữa)
_KING_END_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]

PST: dict[chess.PieceType, list[int]] = {
    chess.PAWN:   _PAWN_TABLE,
    chess.KNIGHT: _KNIGHT_TABLE,
    chess.BISHOP: _BISHOP_TABLE,
    chess.ROOK:   _ROOK_TABLE,
    chess.QUEEN:  _QUEEN_TABLE,
    chess.KING:   _KING_MID_TABLE,  # thay bằng _KING_END_TABLE khi tàn cuộc
}

# ── Heuristic tàn cuộc ────────────────────────────────────────────────────────
def _is_endgame(board: chess.Board) -> bool:
    """Tàn cuộc: mỗi bên không còn Hậu, hoặc tổng vật chất nhỏ."""
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + \
             len(board.pieces(chess.QUEEN, chess.BLACK))
    total  = sum(
        len(board.pieces(pt, c)) * PIECE_VALUES[pt]
        for pt in (chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.QUEEN)
        for c  in (chess.WHITE, chess.BLACK)
    )
    return queens == 0 or total < 1_300


# ── Điểm vị trí quân ─────────────────────────────────────────────────────────
def _pst_score(piece: chess.Piece, square: chess.Square, endgame: bool) -> int:
    table = _KING_END_TABLE if (endgame and piece.piece_type == chess.KING) \
            else PST[piece.piece_type]
    idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
    # PST index 0 = A8 (hàng 8), nhưng chess.square 0 = A1
    # Lật index: idx 0 (A1) → table[56], idx 63 (H8) → table[7]
    return table[idx ^ 56]


# ── C. King Safety ────────────────────────────────────────────────────────────
def _king_safety(board: chess.Board, color: chess.Color) -> int:
    score = 0
    king_sq = board.king(color)
    if king_sq is None:
        return 0

    # Thưởng đã nhập thành
    if color == chess.WHITE:
        if board.has_castling_rights(chess.WHITE):
            score -= 10   # Phạt nhẹ nếu chưa nhập thành mà vẫn còn quyền
        # Kiểm tra vua đã qua nhập thành (vị trí g1 hoặc c1)
        if king_sq in (chess.G1, chess.C1):
            score += 40
    else:
        if board.has_castling_rights(chess.BLACK):
            score -= 10
        if king_sq in (chess.G8, chess.C8):
            score += 40

    # Phạt nếu vua đang bị chiếu
    if board.is_check() and board.turn == color:
        score -= 50

    # Đếm quân phòng thủ xung quanh vua (1 vòng)
    for sq in chess.SquareSet(chess.BB_KING_ATTACKS[king_sq]):
        p = board.piece_at(sq)
        if p and p.color == color:
            score += 10

    return score


# ── D. Pawn Structure ─────────────────────────────────────────────────────────
def _pawn_structure(board: chess.Board, color: chess.Color) -> int:
    score = 0
    pawns = board.pieces(chess.PAWN, color)
    files_with_pawns: dict[int, int] = {}

    for sq in pawns:
        f = chess.square_file(sq)
        files_with_pawns[f] = files_with_pawns.get(f, 0) + 1

    for f, count in files_with_pawns.items():
        # Tốt đôi (doubled pawn)
        if count > 1:
            score -= 20 * (count - 1)
        # Tốt lẻ (isolated pawn)
        if (f - 1) not in files_with_pawns and (f + 1) not in files_with_pawns:
            score -= 15

    # Tốt thông (passed pawn): không bị tốt đối thủ chặn trên cột đó và 2 cột kề
    opp_pawns = board.pieces(chess.PAWN, not color)
    opp_files = {chess.square_file(sq) for sq in opp_pawns}

    for sq in pawns:
        f    = chess.square_file(sq)
        rank = chess.square_rank(sq)
        blocking = {f - 1, f, f + 1} & opp_files
        if not blocking:
            # Thưởng tăng dần theo số hàng đã tiến (Trắng: rank 1→7, Đen: rank 6→0)
            advancement = rank if color == chess.WHITE else (7 - rank)
            score += 20 + advancement * 10

    return score


# ── E. Mobility ───────────────────────────────────────────────────────────────
def _mobility(board: chess.Board, color: chess.Color) -> int:
    board.turn = color
    return len(list(board.legal_moves))


# ── Hàm lượng giá tổng hợp ───────────────────────────────────────────────────
def evaluate(board: chess.Board) -> int:
    """
    Trả về điểm đánh giá theo góc nhìn Trắng (> 0 = Trắng tốt).
    Gọi từ Negamax bằng cách nhân thêm turn_factor.
    """
    if board.is_checkmate():
        # Bên đang có lượt đi bị chiếu bí → thua
        return -CHECKMATE if board.turn == chess.WHITE else CHECKMATE
    if board.is_stalemate() or board.is_insufficient_material() \
            or board.can_claim_draw():
        return DRAW

    endgame = _is_endgame(board)
    score   = 0

    # A + B: Material + PST
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece is None:
            continue
        val = PIECE_VALUES[piece.piece_type] + _pst_score(piece, sq, endgame)
        score += val if piece.color == chess.WHITE else -val

    # C: King Safety
    score += _king_safety(board, chess.WHITE) - _king_safety(board, chess.BLACK)

    # D: Pawn Structure
    score += _pawn_structure(board, chess.WHITE) - _pawn_structure(board, chess.BLACK)

    # E: Mobility (giảm nhẹ ảnh hưởng để không làm chậm quá)
    try:
        mob_w = _mobility(board, chess.WHITE)
        mob_b = _mobility(board, chess.BLACK)
        score += (mob_w - mob_b) * 5
    except Exception:
        pass

    return score

