import sys
import unittest
from pathlib import Path

import numpy as np


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from render_stream_whiteboard import _order_text_cells  # noqa: E402


class TextCellOrderingTests(unittest.TestCase):
    def test_orders_each_line_left_to_right_and_lines_top_to_bottom(self):
        active = np.zeros((8, 8), dtype=bool)
        active[1, [1, 3, 5]] = True
        active[2, [1, 2, 5]] = True
        active[5, [0, 4, 6]] = True
        active[6, [0, 1, 6]] = True

        ordered = _order_text_cells(active)

        self.assertEqual(
            ordered,
            [(1, 1), (2, 1), (2, 2), (1, 3), (1, 5), (2, 5),
             (5, 0), (6, 0), (6, 1), (5, 4), (5, 6), (6, 6)],
        )

    def test_empty_mask_has_no_path(self):
        self.assertEqual(_order_text_cells(np.zeros((3, 4), dtype=bool)), [])


if __name__ == "__main__":
    unittest.main()
