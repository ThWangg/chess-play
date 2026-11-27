"""
BoardWidget: Bàn cờ PySide6 chuẩn quốc tế.
- Bộ quân cburnett (Lichess/FIDE standard).
- Dấu vết di chuyển: highlight + vòng tròn vết chân + mũi tên vector chỉ hướng.
- Tọa độ a-h / 1-8 lồng trong ô rìa, tự đổi màu tương phản.
- Kéo-thả quân cờ, phong cấp tốt, Vua bị chiếu highlight đỏ.
"""
from __future__ import annotations

import math

import chess
from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from .piece_svg import get_svg

# ─── Màu bàn cờ (Tournament Green – chuẩn FIDE) ─────────────────────────────
CLR_LIGHT       = QColor("#EEEED2")   # trắng ngà
CLR_DARK        = QColor("#769656")   # xanh lá thi đấu

# ─── Màu highlight ────────────────────────────────────────────────────────────
CLR_SELECT      = QColor(246, 246, 105, 180)   # vàng chọn ô
CLR_LEGAL_DOT   = QColor(0,   0,   0,  80)     # chấm gợi ý nước đi (tối nhạt)
CLR_LEGAL_RNG   = QColor(0,   0,   0,  80)     # vòng viền ô có quân (ăn được)
CLR_CHECK       = QColor(220,  50,  50, 180)    # Vua bị chiếu
CLR_TRACE_FROM  = QColor(255, 235,  59, 110)    # ô xuất phát – vàng nhạt
CLR_TRACE_TO    = QColor(205, 220,  57, 160)    # ô đích – vàng đậm
CLR_FOOTPRINT   = QColor(180, 150,   0, 100)    # vòng tròn vết chân (ô xuất phát)
CLR_ARROW       = QColor(255, 170,   0, 190)    # màu mũi tên hướng đi
CLR_HINT        = QColor(  0, 188, 212, 160)    # màu gợi ý (xanh ngọc)


def _symbol(piece: chess.Piece) -> str:
    """chess.Piece → key SVG ('wK', 'bP', ...)."""
    color = "w" if piece.color == chess.WHITE else "b"
    return color + piece.symbol().upper()


# ─── Dialog phong cấp tốt ─────────────────────────────────────────────────────
class PromotionDialog(QDialog):
    def __init__(self, color: chess.Color, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Phong cấp tốt")
        self.setModal(True)
        self.setStyleSheet("background:#2c3e50; color:white;")
        self.chosen: chess.PieceType = chess.QUEEN
        layout = QGridLayout(self)
        pieces = [
            (chess.QUEEN,  "Hậu"),
            (chess.ROOK,   "Xe"),
            (chess.BISHOP, "Tượng"),
            (chess.KNIGHT, "Mã"),
        ]
        for col, (ptype, label) in enumerate(pieces):
            sym = ("w" if color == chess.WHITE else "b") + chess.piece_symbol(ptype).upper()
            svg_bytes = get_svg(sym)
            renderer  = QSvgRenderer(QByteArray(svg_bytes))
            px = QPixmap(64, 64)
            px.fill(Qt.transparent)
            p = QPainter(px)
            renderer.render(p)
            p.end()
            btn = QPushButton(label)
            btn.setIcon(px)
            btn.setIconSize(px.size())
            btn.setFixedSize(90, 90)
            btn.setStyleSheet(
                "QPushButton{background:#34495e;border:none;border-radius:6px;color:white;font-size:12px;}"
                "QPushButton:hover{background:#3d6b8e;}"
            )
            btn.clicked.connect(lambda _, pt=ptype: self._pick(pt))
            layout.addWidget(btn, 0, col)

    def _pick(self, ptype: chess.PieceType) -> None:
        self.chosen = ptype
        self.accept()


# ─── BoardWidget ──────────────────────────────────────────────────────────────
class BoardWidget(QWidget):
    """Widget bàn cờ tương tác: quân cburnett + dấu vết + mũi tên vector."""

    move_made = Signal(object)   # chess.Move

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.board              = chess.Board()
        self._selected:   chess.Square | None = None
        self._legal_dsts: set[chess.Square]   = set()
        self._last_move:  chess.Move   | None = None
        self._hint_sq:    chess.Square | None = None
        self._flip         = False
        self._drag_sq:    chess.Square | None = None
        self._drag_pos:   QPointF             = QPointF()
        self._dragging    = False

        self.setMinimumSize(480, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)

    # ── Helpers ───────────────────────────────────────────────────────────────
    @property
    def _sq_size(self) -> float:
        return min(self.width(), self.height()) / 8

    def _sq_to_xy(self, sq: chess.Square) -> tuple[float, float]:
        """Góc trên-trái của ô sq theo pixel."""
        col  = chess.square_file(sq)
        row  = chess.square_rank(sq)
        sz   = self._sq_size
        if not self._flip:
            return col * sz, (7 - row) * sz
        return (7 - col) * sz, row * sz

    def _sq_center(self, sq: chess.Square) -> QPointF:
        x, y = self._sq_to_xy(sq)
        h = self._sq_size / 2
        return QPointF(x + h, y + h)

    def _xy_to_sq(self, x: float, y: float) -> chess.Square | None:
        sz = self._sq_size
        col = int(x / sz)
        row = int(y / sz)
        if not (0 <= col < 8 and 0 <= row < 8):
            return None
        file_ = col if not self._flip else 7 - col
        rank_ = (7 - row) if not self._flip else row
        return chess.square(file_, rank_)

    def _render_piece(self, painter: QPainter, sq: chess.Square, rect: QRectF) -> None:
        piece = self.board.piece_at(sq)
        if piece is None:
            return
        self._render_piece_sym(painter, _symbol(piece), rect)

    def _render_piece_sym(self, painter: QPainter, sym: str, rect: QRectF) -> None:
        renderer = QSvgRenderer(QByteArray(get_svg(sym)), self)
        renderer.render(painter, rect)

    def _select(self, sq: chess.Square) -> None:
        piece = self.board.piece_at(sq)
        if piece and piece.color == self.board.turn:
            self._selected   = sq
            self._legal_dsts = {m.to_square for m in self.board.legal_moves if m.from_square == sq}
        else:
            self._selected   = None
            self._legal_dsts = set()

    def _try_move(self, from_sq: chess.Square, to_sq: chess.Square) -> bool:
        promo = None
        piece = self.board.piece_at(from_sq)
        if piece and piece.piece_type == chess.PAWN:
            rank = chess.square_rank(to_sq)
            if (piece.color == chess.WHITE and rank == 7) or \
               (piece.color == chess.BLACK and rank == 0):
                dlg   = PromotionDialog(piece.color, self)
                dlg.exec()
                promo = dlg.chosen
        move = chess.Move(from_sq, to_sq, promotion=promo)
        if move in self.board.legal_moves:
            self.board.push(move)
            self._last_move  = move
            self._hint_sq    = None
            self._selected   = None
            self._legal_dsts = set()
            self.move_made.emit(move)
            self.update()
            return True
        return False

    # ── Public API ────────────────────────────────────────────────────────────
    def flip(self) -> None:
        self._flip = not self._flip
        self.update()

    def reset(self) -> None:
        self.board.reset()
        self._selected   = None
        self._legal_dsts = set()
        self._last_move  = None
        self._hint_sq    = None
        self._dragging   = False
        self._drag_sq    = None
        self._flip       = False
        self.update()

    def load_fen(self, fen: str, flip: bool = False) -> None:
        """Nạp thế cờ từ chuỗi FEN (dùng cho chế độ Thế cờ tàn)."""
        self.board.set_fen(fen)
        self._selected   = None
        self._legal_dsts = set()
        self._last_move  = None
        self._hint_sq    = None
        self._dragging   = False
        self._drag_sq    = None
        self._flip       = flip
        self.update()

    def show_hint(self, sq: chess.Square | None) -> None:
        """Highlight ô gợi ý quân cần đi."""
        self._hint_sq = sq
        self.update()

    def apply_move(self, move: chess.Move) -> None:
        """Áp dụng nước đi từ AI (không emit move_made để tránh vòng lặp)."""
        if move in self.board.legal_moves:
            self.board.push(move)
            self._last_move  = move
            self._hint_sq    = None
            self._selected   = None
            self._legal_dsts = set()
            self.update()

    # ── paintEvent ────────────────────────────────────────────────────────────
    def paintEvent(self, _event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        sz = self._sq_size

        for sq in chess.SQUARES:
            x, y  = self._sq_to_xy(sq)
            rect  = QRectF(x, y, sz, sz)
            file_ = chess.square_file(sq)
            rank_ = chess.square_rank(sq)

            # 1. Nền ô (sáng / tối)
            is_light = (file_ + rank_) % 2 == 1
            painter.fillRect(rect, CLR_LIGHT if is_light else CLR_DARK)

            # 2. Dấu vết di chuyển
            if self._last_move:
                if sq == self._last_move.from_square:
                    painter.fillRect(rect, CLR_TRACE_FROM)
                elif sq == self._last_move.to_square:
                    painter.fillRect(rect, CLR_TRACE_TO)

            # 3. Highlight ô được chọn & ô gợi ý
            if sq == self._hint_sq:
                painter.fillRect(rect, CLR_HINT)
            if sq == self._selected:
                painter.fillRect(rect, CLR_SELECT)

            # 4. Highlight Vua bị chiếu
            if self.board.is_check():
                king_sq = self.board.king(self.board.turn)
                if sq == king_sq:
                    painter.fillRect(rect, CLR_CHECK)

            # 5. Vẽ quân cờ (bỏ qua quân đang kéo)
            if sq != self._drag_sq or not self._dragging:
                self._render_piece(painter, sq, rect.adjusted(3, 3, -3, -3))

            # 6. Chấm / viền gợi ý nước đi hợp lệ
            if sq in self._legal_dsts:
                piece_at_dst = self.board.piece_at(sq)
                if piece_at_dst:
                    # Vòng viền cho ô có quân đối thủ (có thể ăn)
                    pen = QPen(CLR_LEGAL_RNG, sz * 0.09)
                    painter.setPen(pen)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(rect.adjusted(4, 4, -4, -4))
                else:
                    # Chấm tròn tâm ô trống
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(CLR_LEGAL_DOT)
                    r  = sz * 0.16
                    cx, cy = x + sz / 2, y + sz / 2
                    painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # 7. Vẽ vết chân ô xuất phát (footprint circle)
        if self._last_move:
            self._draw_trace_footprint(painter, self._last_move.from_square)
            # 8. Mũi tên vector chỉ hướng đi
            self._draw_move_arrow(painter, self._last_move.from_square, self._last_move.to_square)

        # 9. Tọa độ a-h / 1-8 lồng trong ô rìa
        self._draw_coordinates(painter)

        # 10. Quân đang kéo theo con trỏ chuột
        if self._dragging and self._drag_sq is not None:
            piece = self.board.piece_at(self._drag_sq)
            if piece:
                half      = sz / 2
                drag_rect = QRectF(
                    self._drag_pos.x() - half,
                    self._drag_pos.y() - half,
                    sz, sz,
                )
                self._render_piece_sym(painter, _symbol(piece), drag_rect.adjusted(3, 3, -3, -3))

        painter.end()

    # ── Vẽ vết chân (footprint) ───────────────────────────────────────────────
    def _draw_trace_footprint(self, painter: QPainter, sq: chess.Square) -> None:
        """Vẽ vòng tròn mờ ở tâm ô xuất phát – dấu vết quân vừa rời đi."""
        sz    = self._sq_size
        cx, cy = (c + sz / 2 for c in self._sq_to_xy(sq))
        r     = sz * 0.28
        painter.setPen(QPen(CLR_FOOTPRINT, sz * 0.055))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

    # ── Vẽ mũi tên vector chỉ hướng đi ──────────────────────────────────────
    def _draw_move_arrow(self, painter: QPainter, from_sq: chess.Square, to_sq: chess.Square) -> None:
        """Vẽ mũi tên bán trong suốt từ tâm ô xuất phát đến tâm ô đích."""
        if from_sq == to_sq:
            return
        sz   = self._sq_size
        p1   = self._sq_center(from_sq)
        p2   = self._sq_center(to_sq)
        shaft_w = max(4.0, sz * 0.13)   # độ dày thân mũi tên
        head_w  = shaft_w * 2.8         # chiều rộng đầu mũi tên
        head_len = shaft_w * 3.0        # chiều dài đầu mũi tên

        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.hypot(dx, dy)
        if length < 1:
            return

        # Vector đơn vị
        ux, uy = dx / length, dy / length
        # Vuông góc
        px, py = -uy, ux

        # Rút ngắn điểm đầu và cuối vào trong ô 20%
        inset = sz * 0.20
        s = QPointF(p1.x() + ux * inset, p1.y() + uy * inset)
        e = QPointF(p2.x() - ux * inset, p2.y() - uy * inset)

        # Điểm bắt đầu đầu mũi tên
        arrow_base = QPointF(e.x() - ux * head_len, e.y() - uy * head_len)

        # Tạo path
        path = QPainterPath()
        # Thân mũi tên (hình chữ nhật mảnh)
        path.moveTo(s.x() + px * shaft_w / 2, s.y() + py * shaft_w / 2)
        path.lineTo(arrow_base.x() + px * shaft_w / 2, arrow_base.y() + py * shaft_w / 2)
        # Đầu mũi tên (tam giác)
        path.lineTo(arrow_base.x() + px * head_w / 2, arrow_base.y() + py * head_w / 2)
        path.lineTo(e.x(), e.y())
        path.lineTo(arrow_base.x() - px * head_w / 2, arrow_base.y() - py * head_w / 2)
        path.lineTo(arrow_base.x() - px * shaft_w / 2, arrow_base.y() - py * shaft_w / 2)
        path.lineTo(s.x() - px * shaft_w / 2, s.y() - py * shaft_w / 2)
        path.closeSubpath()

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(CLR_ARROW))
        painter.drawPath(path)

    # ── Vẽ tọa độ lồng trong ô rìa ───────────────────────────────────────────
    def _draw_coordinates(self, painter: QPainter) -> None:
        """Vẽ a-h ở góc dưới-phải hàng cuối, 1-8 ở góc trên-trái cột đầu."""
        sz    = self._sq_size
        font  = QFont("Segoe UI", max(7, int(sz * 0.19)), QFont.Bold)
        painter.setFont(font)
        files = "abcdefgh"
        ranks = "12345678"

        for i in range(8):
            sq_col = i if not self._flip else 7 - i
            sq_row = i if not self._flip else 7 - i

            # Chữ cái cột (a-h) ở góc dưới-phải ô hàng 1 (rank 0)
            sq_f = chess.square(sq_col, 0 if not self._flip else 7)
            bx, by = self._sq_to_xy(sq_f)
            is_light_f = (chess.square_file(sq_f) + chess.square_rank(sq_f)) % 2 == 1
            painter.setPen(CLR_DARK if is_light_f else CLR_LIGHT)
            painter.drawText(
                QRectF(bx + sz * 0.60, by + sz * 0.60, sz * 0.37, sz * 0.37),
                Qt.AlignCenter, files[sq_col],
            )

            # Chữ số hàng (1-8) ở góc trên-trái ô cột a (file 0)
            sq_r = chess.square(0 if not self._flip else 7, sq_row)
            lx, ly = self._sq_to_xy(sq_r)
            is_light_r = (chess.square_file(sq_r) + chess.square_rank(sq_r)) % 2 == 1
            painter.setPen(CLR_DARK if is_light_r else CLR_LIGHT)
            painter.drawText(
                QRectF(lx + sz * 0.03, ly + sz * 0.03, sz * 0.35, sz * 0.35),
                Qt.AlignCenter, ranks[sq_row],
            )

    # ── Mouse events ──────────────────────────────────────────────────────────
    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton:
            return
        sq = self._xy_to_sq(event.position().x(), event.position().y())
        if sq is None:
            return
        piece = self.board.piece_at(sq)
        if piece and piece.color == self.board.turn:
            self._drag_sq  = sq
            self._drag_pos = event.position()
            self._dragging = False
            self._select(sq)
            self.update()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._drag_sq is not None:
            self._dragging = True
            self._drag_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton:
            return
        to_sq = self._xy_to_sq(event.position().x(), event.position().y())

        if self._dragging and self._drag_sq is not None and to_sq is not None:
            if to_sq != self._drag_sq:
                self._try_move(self._drag_sq, to_sq)
        elif not self._dragging and self._drag_sq is None:
            if to_sq is not None:
                if self._selected is not None and to_sq in self._legal_dsts:
                    self._try_move(self._selected, to_sq)
                else:
                    self._select(to_sq)

        if not self._dragging and self._drag_sq is not None:
            if to_sq is not None:
                if self._selected == self._drag_sq and to_sq in self._legal_dsts:
                    self._try_move(self._drag_sq, to_sq)

        self._dragging = False
        self._drag_sq  = None
        self.update()
