"""
Unit tests cho kho thế cờ tàn (Endgame Mate-in-1 puzzles).
Đảm bảo tất cả FEN đều hợp lệ và có ít nhất 1 nước chiếu hết ngay lập tức.
"""
import unittest
import chess

from src.core.constants import EndgameLevel
from src.core.puzzles import PUZZLES, find_mate_in_1_move, get_puzzles_by_level


class TestEndgamePuzzles(unittest.TestCase):
    def test_all_levels_populated(self) -> None:
        for level in EndgameLevel.LABELS:
            puzzles = get_puzzles_by_level(level)
            self.assertGreaterEqual(
                len(puzzles), 5, f"Level {level} cần tối thiểu 5 thế cờ"
            )

    def test_all_puzzles_valid_and_mate_in_1(self) -> None:
        for puzzle in PUZZLES:
            board = chess.Board(puzzle.fen)
            self.assertTrue(
                board.is_valid(), f"FEN không hợp lệ ở {puzzle.id}: {puzzle.fen}"
            )
            self.assertFalse(
                board.is_game_over(), f"Ván cờ đã kết thúc sẵn ở {puzzle.id}"
            )
            mate_move = find_mate_in_1_move(board)
            self.assertIsNotNone(
                mate_move, f"Không tìm thấy nước chiếu hết 1 nước ở {puzzle.id}"
            )


if __name__ == "__main__":
    unittest.main()
