"""
Kho dữ liệu thế cờ tàn (Mate in 1, 2, 3, 4) và bộ giải Forced-Mate chính xác.
- Cấp 1: Chiếu hết trong 1 nước
- Cấp 2: Chiếu hết trong 2 nước
- Cấp 3: Chiếu hết trong 3 nước
- Cấp 4: Chiếu hết trong 4 nước
"""
from __future__ import annotations

from dataclasses import dataclass
import chess

from src.core.constants import EndgameLevel


@dataclass(frozen=True)
class EndgamePuzzle:
    id: str
    level: int          # Số nước tối đa để chiếu hết (1, 2, 3, 4)
    title: str
    fen: str
    hint: str


# ── Bộ giải Forced-Mate (Mate in N) ───────────────────────────────────────────
def _order_forcing_moves(board: chess.Board) -> list[chess.Move]:
    """Ưu tiên nước chiếu, phong cấp, ăn quân để tìm forced mate siêu nhanh."""
    def _key(m: chess.Move) -> int:
        s = 0
        if board.gives_check(m):
            s += 100
        if m.promotion:
            s += 50
        if board.is_capture(m):
            s += 20
        return s

    return sorted(board.legal_moves, key=_key, reverse=True)


def _can_force_mate(
    board: chess.Board,
    plies_left: int,
    is_attacker: bool,
    memo: dict[tuple, bool],
) -> bool:
    """
    Kiểm tra bên tấn công có ép chiếu hết được trong <= plies_left ply không.
    - plies_left = 1 nghĩa là attacker đi 1 nước phải mate ngay.
    - plies_left = 3 nghĩa là attacker(1) -> defender(1) -> attacker(1) = mate.
    """
    if board.is_checkmate():
        return not is_attacker  # attacker vừa đi xong và tạo ra checkmate
    if board.is_game_over() or plies_left <= 0:
        return False

    key = (board._transposition_key(), plies_left, is_attacker)
    if key in memo:
        return memo[key]

    if is_attacker:
        for move in _order_forcing_moves(board):
            # Ở ply cuối cùng, chỉ xét các nước chiếu
            if plies_left == 1 and not board.gives_check(move):
                continue
            board.push(move)
            ok = _can_force_mate(board, plies_left - 1, False, memo)
            board.pop()
            if ok:
                memo[key] = True
                return True
        memo[key] = False
        return False
    else:
        # Defender: chỉ cần tồn tại 1 nước thoát được (không bị mate) -> False
        moves = list(board.legal_moves)
        if not moves:
            memo[key] = False
            return False
        for move in moves:
            board.push(move)
            ok = _can_force_mate(board, plies_left - 1, True, memo)
            board.pop()
            if not ok:
                memo[key] = False
                return False
        memo[key] = True
        return True


def find_forced_mate_move(board: chess.Board, max_moves: int) -> chess.Move | None:
    """
    Tìm nước đi cho bên tấn công để ép chiếu hết trong <= max_moves nước.
    Trả về None nếu không có nước đi nào ép chiếu hết được.
    """
    if max_moves <= 0 or board.is_game_over():
        return None
    plies = max_moves * 2 - 1
    memo: dict[tuple, bool] = {}
    for move in _order_forcing_moves(board):
        if plies == 1 and not board.gives_check(move):
            continue
        board.push(move)
        ok = _can_force_mate(board, plies - 1, False, memo)
        board.pop()
        if ok:
            return move
    return None


def is_winning_mate_move(board_after_move: chess.Board, remaining_moves: int) -> bool:
    """
    Sau khi người chơi vừa đi, kiểm tra từ thế cờ mới (lượt của defender)
    bên tấn công vẫn còn ép được chiếu hết trong <= remaining_moves nước.
    """
    if board_after_move.is_checkmate():
        return True
    if remaining_moves <= 0 or board_after_move.is_game_over():
        return False
    memo: dict[tuple, bool] = {}
    plies = remaining_moves * 2  # defender đi 1 ply + remaining_moves*2 - 1
    return _can_force_mate(board_after_move, plies, False, memo)


def find_defender_response(board: chess.Board, remaining_moves: int) -> chess.Move | None:
    """
    Tìm nước chống đỡ tốt nhất (kéo dài số nước lâu nhất) cho bên phòng thủ.
    """
    legal = list(board.legal_moves)
    if not legal:
        return None
    if len(legal) == 1:
        return legal[0]

    # Tìm nước khiến attacker cần nhiều nước nhất (hoặc thoát được)
    best_move = legal[0]
    best_resistance = -1
    memo: dict[tuple, bool] = {}

    for move in legal:
        board.push(move)
        # Thử xem attacker có mate được trong 1, 2, ..., remaining_moves nước không
        resistance = remaining_moves + 1
        for m in range(1, remaining_moves + 1):
            if _can_force_mate(board, m * 2 - 1, True, memo):
                resistance = m
                break
        board.pop()
        if resistance > best_resistance:
            best_resistance = resistance
            best_move = move
            if best_resistance > remaining_moves:
                break

    return best_move


# ── Kho thế cờ tàn 4 cấp độ ──────────────────────────────────────────────────
PUZZLES: list[EndgamePuzzle] = [
    # ── CẤP 1: CHIẾU HẾT TRONG 1 NƯỚC (Mate in 1) ─────────────────────────────
    EndgamePuzzle(
        id="M1_01",
        level=EndgameLevel.MATE_1,
        title="Hậu + Vua chiếu hết hàng cuối",
        fen="4k3/8/4K3/8/8/8/7Q/8 w - - 0 1",
        hint="Đưa Hậu lên hàng ngang số 8 (h8) để chiếu hết.",
    ),
    EndgamePuzzle(
        id="M1_02",
        level=EndgameLevel.MATE_1,
        title="Chiếu hết hàng cuối (Back Rank)",
        fen="6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1",
        hint="Xe trượt thẳng xuống hàng ngang số 8.",
    ),
    EndgamePuzzle(
        id="M1_03",
        level=EndgameLevel.MATE_1,
        title="Xe + Mã khóa góc (Arabian Mate)",
        fen="7k/R7/5N2/8/8/8/8/6K1 w - - 0 1",
        hint="Mã f6 bảo vệ ô h7 và chặn g8, đưa Xe sang h7.",
    ),
    EndgamePuzzle(
        id="M1_04",
        level=EndgameLevel.MATE_1,
        title="Chiếu bí thắt cổ (Smothered Mate)",
        fen="6rk/6pp/8/4N3/8/8/8/6K1 w - - 0 1",
        hint="Vua Đen bị bịt kín bởi Xe và Tốt, nhảy Mã vào f7.",
    ),
    EndgamePuzzle(
        id="M1_05",
        level=EndgameLevel.MATE_1,
        title="Phong cấp thành Mã chiếu hết",
        fen="6nb/5Ppk/8/6K1/8/8/8/8 w - - 0 1",
        hint="Tốt f7 tiến lên f8 phong cấp thành Mã mới chiếu hết được!",
    ),

    # ── CẤP 2: CHIẾU HẾT TRONG 2 NƯỚC (Mate in 2) ─────────────────────────────
    EndgamePuzzle(
        id="M2_01",
        level=EndgameLevel.MATE_2,
        title="Đẩy Vua vào góc (Hậu + Vua)",
        fen="6k1/8/6K1/8/8/8/3Q4/8 w - - 0 1",
        hint="Đưa Hậu cắt hàng 7 hoặc chiếu ở d8/a2 để ép Vua vào góc rồi chiếu hết.",
    ),
    EndgamePuzzle(
        id="M2_02",
        level=EndgameLevel.MATE_2,
        title="Thí Hậu mở đường hàng cuối",
        fen="5rk1/5ppp/8/8/8/4Q3/8/4R1K1 w - - 0 1",
        hint="Thí Hậu vào e8 buộc Xe Đen ăn, sau đó Xe e1 xuống chiếu hết!",
    ),
    EndgamePuzzle(
        id="M2_03",
        level=EndgameLevel.MATE_2,
        title="Hai Xe cắt thang (Ladder Mate)",
        fen="4k3/8/8/8/8/R7/1R6/4K3 w - - 0 1",
        hint="Đưa 1 Xe lên hàng 7 cắt đường Vua, nước sau Xe kia lên hàng 8.",
    ),
    EndgamePuzzle(
        id="M2_04",
        level=EndgameLevel.MATE_2,
        title="Anastasia's Mate (2 nước)",
        fen="5r1k/4N1pp/8/8/8/8/8/4R1K1 w - - 0 1",
        hint="Mã e7 đã khóa cột g, Xe ăn tốt h7? Không, đưa Xe sang cột h hoặc thí Hậu/Xe!",
    ),
    EndgamePuzzle(
        id="M2_05",
        level=EndgameLevel.MATE_2,
        title="Đen đi: Thí Hậu chiếu bí thắt cổ",
        fen="r5k1/5ppp/8/8/8/8/5PPP/3q1RK1 b - - 0 1",
        hint="Tìm đòn phối hợp ở hàng 1!",
    ),

    # ── CẤP 3: CHIẾU HẾT TRONG 3 NƯỚC (Mate in 3) ─────────────────────────────
    EndgamePuzzle(
        id="M3_01",
        level=EndgameLevel.MATE_3,
        title="Ép Vua vào cạnh bằng Xe + Vua",
        fen="4k3/8/4K3/8/8/8/R7/8 w - - 0 1",
        hint="Dùng nước chờ của Xe hoặc đẩy Vua Đen sát mép bàn cờ để chiếu hết trong 3 nước.",
    ),
    EndgamePuzzle(
        id="M3_02",
        level=EndgameLevel.MATE_3,
        title="Hai Xe săn Vua từ trung tâm",
        fen="8/8/4k3/8/8/8/R7/1R2K3 w - - 0 1",
        hint="Dùng 2 Xe thay phiên nhau chiếu, đẩy Vua Đen lên hàng 8.",
    ),
    EndgamePuzzle(
        id="M3_03",
        level=EndgameLevel.MATE_3,
        title="Hậu + Tốt dứt điểm",
        fen="7k/8/5K2/6P1/8/8/8/3Q4 w - - 0 1",
        hint="Đẩy Tốt hoặc đưa Hậu khép góc h8.",
    ),
    EndgamePuzzle(
        id="M3_04",
        level=EndgameLevel.MATE_3,
        title="Xe + Tượng vây hãm góc",
        fen="6k1/8/5K2/8/8/2B5/8/4R3 w - - 0 1",
        hint="Phối hợp Xe và Tượng khống chế các ô thoát trước khi chiếu hết.",
    ),

    # ── CẤP 4: CHIẾU HẾT TRONG 4 NƯỚC (Mate in 4) ─────────────────────────────
    EndgamePuzzle(
        id="M4_01",
        level=EndgameLevel.MATE_4,
        title="Vua + Xe dồn góc kinh điển (4 nước)",
        fen="3k4/8/3K4/8/8/8/8/R7 w - - 0 1",
        hint="Chặn hàng/cột và dùng nước chờ (tempo) để ép Vua Đen vào góc.",
    ),
    EndgamePuzzle(
        id="M4_02",
        level=EndgameLevel.MATE_4,
        title="Hậu + Mã truy sát (4 nước)",
        fen="6k1/5p2/6p1/8/8/5N2/8/3Q2K1 w - - 0 1",
        hint="Đưa Hậu và Mã áp sát cánh Vua để tung đòn chiếu liên hoàn.",
    ),
    EndgamePuzzle(
        id="M4_03",
        level=EndgameLevel.MATE_4,
        title="Cặp Xe + Vua khóa chặt (4 nước)",
        fen="8/8/8/4k3/8/8/R7/1R2K3 w - - 0 1",
        hint="Chiếu từng hàng ngang để đẩy Vua từ giữa bàn cờ lên hàng 8.",
    ),
    EndgamePuzzle(
        id="M4_04",
        level=EndgameLevel.MATE_4,
        title="Hậu đơn thương độc mã dồn góc (4 nước)",
        fen="8/8/4k3/8/4K3/8/8/3Q4 w - - 0 1",
        hint="Dùng nước nhảy Mã của Hậu để khép dần không gian của Vua Đen.",
    ),
]


def get_puzzles_by_level(level: int) -> list[EndgamePuzzle]:
    """Trả về danh sách các thế cờ tàn theo cấp độ."""
    return [p for p in PUZZLES if p.level == level]
