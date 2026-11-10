"""
BoardWidget: Bàn cờ PySide6 hỗ trợ kéo-thả quân cờ.
- Hiển thị bàn cờ 8x8 với màu xen kẽ.
- Highlight ô được chọn (vàng) + các ô đi hợp lệ (chấm tròn xanh).
- Kéo-thả quân cờ hoàn toàn bằng chuột.
- Phong cấp tốt: hiện dialog chọn quân.
- Hiển thị ký hiệu hàng/cột bên ngoài bàn cờ.
- Signal: move_made(chess.Move) khi đi xong 1 nước.
"""
from __future__ import annotations

import chess
from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
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

# ─── màu ─────────────────────────────────────────────────────────────────────
CLR_LIGHT   = QColor("#F0D9B5")
CLR_DARK    = QColor("#B58863")
CLR_SELECT  = QColor(246, 246, 105, 180)   # vàng trong suốt
CLR_LEGAL   = QColor(20, 85, 30, 128)      # chấm xanh đậm
CLR_LAST_MV = QColor(205, 210, 106, 160)   # highlight nước vừa đi
CLR_CHECK   = QColor(220, 50, 50, 180)     # Vua bị chiếu


def _symbol(piece: chess.Piece) -> str:
    """Chuyển chess.Piece -> key SVG (vd: 'wK', 'bP')."""
    color = "w" if piece.color == chess.WHITE else "b"
    return color + piece.symbol().upper()


class PromotionDialog(QDialog):
    """Popup chọn quân phong cấp tốt."""

    def __init__(self, color: chess.Color, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Phong cấp tốt")
        self.setModal(True)
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
            renderer = QSvgRenderer(QByteArray(svg_bytes))
            px = QPixmap(64, 64)
            px.fill(Qt.transparent)
            painter = QPainter(px)
            renderer.render(painter)
            painter.end()

            btn = QPushButton(label)
            btn.setIcon(px)
            btn.setIconSize(px.size())
            btn.setFixedSize(90, 90)
            btn.clicked.connect(lambda _, pt=ptype: self._pick(pt))
            layout.addWidget(btn, 0, col)

    def _pick(self, ptype: chess.PieceType) -> None:
        self.chosen = ptype
        self.accept()


class BoardWidget(QWidget):
    """Widget bàn cờ tương tác: kéo-thả, highlight, phong cấp tốt."""

    move_made = Signal(object)  # chess.Move

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.board = chess.Board()
        self._selected: chess.Square | None = None
        self._legal_dsts: set[chess.Square] = set()
        self._last_move: chess.Move | None = None
        self._flip = False          # True = nhìn từ phía Đen
        self._drag_sq: chess.Square | None = None   # ô đang kéo
        self._drag_pos: QPointF = QPointF()         # vị trí chuột khi kéo
        self._dragging = False

        self.setMinimumSize(480, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)

    # ── helpers ──────────────────────────────────────────────────────────────
    @property
    def _sq_size(self) -> float:
        return min(self.width(), self.height()) / 8

    def _sq_to_xy(self, sq: chess.Square) -> tuple[float, float]:
        """Góc trên-trái của ô sq theo pixel."""
        col = chess.square_file(sq)
        row = chess.square_rank(sq)
        if not self._flip:
            x = col * self._sq_size
            y = (7 - row) * self._sq_size
        else:
            x = (7 - col) * self._sq_size
            y = row * self._sq_size
        return x, y

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
        sym = _symbol(piece)
        svg_bytes = get_svg(sym)
        renderer = QSvgRenderer(QByteArray(svg_bytes), self)
        renderer.render(painter, rect)

    def _select(self, sq: chess.Square) -> None:
        piece = self.board.piece_at(sq)
        if piece and piece.color == self.board.turn:
            self._selected = sq
            self._legal_dsts = {
                m.to_square for m in self.board.legal_moves if m.from_square == sq
            }
        else:
            self._selected = None
            self._legal_dsts = set()

    def _try_move(self, from_sq: chess.Square, to_sq: chess.Square) -> bool:
        """Thực hiện nước đi (kể cả phong cấp tốt). Trả về True nếu thành công."""
        promo = None
        piece = self.board.piece_at(from_sq)
        if piece and piece.piece_type == chess.PAWN:
            rank = chess.square_rank(to_sq)
            if (piece.color == chess.WHITE and rank == 7) or \
               (piece.color == chess.BLACK and rank == 0):
                dlg = PromotionDialog(piece.color, self)
                dlg.exec()
                promo = dlg.chosen

        move = chess.Move(from_sq, to_sq, promotion=promo)
        if move in self.board.legal_moves:
            self.board.push(move)
            self._last_move = move
            self._selected = None
            self._legal_dsts = set()
            self.move_made.emit(move)
            self.update()
            return True
        return False

    # ── Flip bàn cờ ──────────────────────────────────────────────────────────
    def flip(self) -> None:
        self._flip = not self._flip
        self.update()

    # ── Reset ────────────────────────────────────────────────────────────────
    def reset(self) -> None:
        self.board.reset()
        self._selected = None
        self._legal_dsts = set()
        self._last_move = None
        self._dragging = False
        self._drag_sq = None
        self.update()

    # ── paintEvent ───────────────────────────────────────────────────────────
    def paintEvent(self, _event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        sz = self._sq_size

        for sq in chess.SQUARES:
            x, y = self._sq_to_xy(sq)
            rect = QRectF(x, y, sz, sz)
            file_ = chess.square_file(sq)
            rank_ = chess.square_rank(sq)

            # nền ô
            is_light = (file_ + rank_) % 2 == 1
            base_color = CLR_LIGHT if is_light else CLR_DARK
            painter.fillRect(rect, base_color)

            # highlight nước vừa đi
            if self._last_move and sq in (self._last_move.from_square, self._last_move.to_square):
                painter.fillRect(rect, CLR_LAST_MV)

            # highlight ô được chọn
            if sq == self._selected:
                painter.fillRect(rect, CLR_SELECT)

            # highlight Vua bị chiếu
            if self.board.is_check():
                king_sq = self.board.king(self.board.turn)
                if sq == king_sq:
                    painter.fillRect(rect, CLR_CHECK)

            # vẽ quân (bỏ qua quân đang kéo)
            if sq != self._drag_sq or not self._dragging:
                self._render_piece(painter, sq, rect.adjusted(2, 2, -2, -2))

            # chấm tròn ô đi hợp lệ
            if sq in self._legal_dsts:
                piece_at_dst = self.board.piece_at(sq)
                if piece_at_dst:
                    # ô có quân đối thủ: vẽ vòng viền
                    pen = QPen(CLR_LEGAL, sz * 0.08)
                    painter.setPen(pen)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawEllipse(rect.adjusted(3, 3, -3, -3))
                else:
                    # ô trống: chấm nhỏ trung tâm
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(CLR_LEGAL)
                    r = sz * 0.17
                    cx, cy = x + sz / 2, y + sz / 2
                    painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # ký hiệu hàng / cột
        font = QFont("Arial", max(8, int(sz * 0.18)), QFont.Bold)
        painter.setFont(font)
        files = "abcdefgh"
        ranks = "12345678"
        for i in range(8):
            sq_col = i if not self._flip else 7 - i
            sq_row = 7 - i if not self._flip else i
            x0, y0 = i * sz, i * sz

            # file label (a-h) dưới góc phải mỗi ô hàng cuối
            sq_bottom = chess.square(sq_col, 0) if not self._flip else chess.square(sq_col, 7)
            bx, by = self._sq_to_xy(sq_bottom)
            is_light_bottom = (chess.square_file(sq_bottom) + chess.square_rank(sq_bottom)) % 2 == 1
            painter.setPen(CLR_DARK if is_light_bottom else CLR_LIGHT)
            painter.drawText(
                QRectF(bx + sz - sz * 0.28, by + sz - sz * 0.28, sz * 0.26, sz * 0.26),
                Qt.AlignCenter, files[sq_col],
            )

            # rank label (1-8) góc trên-trái mỗi ô cột đầu
            sq_left = chess.square(0, sq_row) if not self._flip else chess.square(7, sq_row)
            lx, ly = self._sq_to_xy(sq_left)
            is_light_left = (chess.square_file(sq_left) + chess.square_rank(sq_left)) % 2 == 1
            painter.setPen(CLR_DARK if is_light_left else CLR_LIGHT)
            painter.drawText(
                QRectF(lx + sz * 0.03, ly + sz * 0.03, sz * 0.26, sz * 0.26),
                Qt.AlignCenter, ranks[sq_row],
            )

        # vẽ quân đang kéo theo con trỏ
        if self._dragging and self._drag_sq is not None:
            piece = self.board.piece_at(self._drag_sq)
            if piece:
                half = sz / 2
                drag_rect = QRectF(
                    self._drag_pos.x() - half,
                    self._drag_pos.y() - half,
                    sz, sz,
                )
                self._render_piece_sym(painter, _symbol(piece), drag_rect.adjusted(2, 2, -2, -2))

        painter.end()

    def _render_piece_sym(self, painter: QPainter, sym: str, rect: QRectF) -> None:
        renderer = QSvgRenderer(QByteArray(get_svg(sym)), self)
        renderer.render(painter, rect)

    # ── Mouse events ─────────────────────────────────────────────────────────
    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton:
            return
        sq = self._xy_to_sq(event.position().x(), event.position().y())
        if sq is None:
            return
        piece = self.board.piece_at(sq)
        if piece and piece.color == self.board.turn:
            self._drag_sq = sq
            self._drag_pos = event.position()
            self._dragging = False          # sẽ bật khi di chuyển
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
            else:
                # thả lại ô cũ = chỉ chọn, không đi
                pass
        elif not self._dragging and self._drag_sq is None:
            # click thuần (không kéo)
            if to_sq is not None:
                if self._selected is not None and to_sq in self._legal_dsts:
                    self._try_move(self._selected, to_sq)
                else:
                    self._select(to_sq)

        # click + không kéo nhưng có drag_sq => click chọn/đổi quân
        if not self._dragging and self._drag_sq is not None:
            if to_sq is not None:
                if self._selected == self._drag_sq and to_sq in self._legal_dsts:
                    self._try_move(self._drag_sq, to_sq)
                # else: giữ chọn hiện tại

        self._dragging = False
        self._drag_sq = None
        self.update()
