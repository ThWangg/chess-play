"""
Hằng số toàn cục cho Chess Application.
"""
from __future__ import annotations

import chess

# ── Chế độ chơi ───────────────────────────────────────────────────────────────
class GameMode:
    PVP     = "pvp"       # Người vs Người
    PVE     = "pve"       # Người vs Máy
    ENDGAME = "endgame"   # Thế cờ tàn (Chiếu hết trong 1 nước)


# ── Cấp độ Thế cờ tàn ─────────────────────────────────────────────────────────
class EndgameLevel:
    MATE_1 = 1   # Chiếu hết trong 1 nước
    MATE_2 = 2   # Chiếu hết trong 2 nước
    MATE_3 = 3   # Chiếu hết trong 3 nước
    MATE_4 = 4   # Chiếu hết trong 4 nước

    LABELS: dict[int, str] = {
        1: "🟢 Cấp 1: Chiếu hết 1 nước",
        2: "🟡 Cấp 2: Chiếu hết 2 nước",
        3: "🟠 Cấp 3: Chiếu hết 3 nước",
        4: "🔴 Cấp 4: Chiếu hết 4 nước",
    }


# ── Cấp độ AI ─────────────────────────────────────────────────────────────────
class AiLevel:
    BEGINNER  = 1   # Random + Minimax depth 1
    EASY      = 2   # Minimax depth 2
    MEDIUM    = 3   # Alpha-Beta depth 3
    HARD      = 4   # Alpha-Beta + Quiescence depth 4
    EXPERT    = 5   # Iterative Deepening + NegaScout, time-limited

    LABELS: dict[int, str] = {
        1: "🟢 Mới bắt đầu",
        2: "🟡 Dễ",
        3: "🟠 Trung bình",
        4: "🔴 Khó",
        5: "🔵 Chuyên gia",
    }

    # Độ sâu tìm kiếm tương ứng (dùng cho alpha-beta thuần)
    DEPTH: dict[int, int] = {
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 6,  # IDDFS sẽ tự điều chỉnh theo thời gian
    }

    # Giới hạn thời gian (giây) cho IDDFS ở cấp 5
    TIME_LIMIT: dict[int, float] = {
        5: 3.0,
    }


# ── Giá trị quân cờ (centipawns) ──────────────────────────────────────────────
PIECE_VALUES: dict[chess.PieceType, int] = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   20_000,
}

# ── Hằng số tìm kiếm ──────────────────────────────────────────────────────────
INF         = 1_000_000   # Vô cực (thay thế float('inf') để dùng int)
CHECKMATE   =   999_999   # Điểm chiếu bí (giảm theo depth để ưu tiên checkmate nhanh hơn)
DRAW        =         0   # Điểm hòa

# Quiescence Search max depth (tránh bùng nổ ở cuối cây)
QDEPTH_MAX  = 4

# Số Killer Moves lưu mỗi độ sâu
KILLER_SLOTS = 2

# ── Màu sắc UI (dùng cho board_widget và style sheet) ─────────────────────────
CLR_LIGHT       = "#F0D9B5"
CLR_DARK        = "#B58863"
CLR_SELECT      = "rgba(246,246,105,180)"
CLR_LEGAL       = "rgba(20,85,30,128)"
CLR_LAST_MOVE   = "rgba(205,210,106,160)"
CLR_CHECK       = "rgba(220,50,50,180)"
CLR_BG_DARK     = "#1a1a2e"
CLR_BG_PANEL    = "#16213e"

