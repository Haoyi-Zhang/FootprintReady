"""Standard-library checks for the retained interval plotting input."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("interval_plot", ROOT / "scripts/draw_interval_costs.py")
plot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plot)


class IntervalPlotInputTests(unittest.TestCase):
    def test_current_archived_rows(self):
        self.assertEqual(plot.load_intervals(ROOT / "results/interval-costs.csv"), plot.EXPECTED)

    def test_changed_row_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intervals.csv"
            path.write_text("radius,lower,upper\n0,67,67\n1,44,92\n3,28,140\n7,4,237\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                plot.load_intervals(path)

    def test_missing_row_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intervals.csv"
            path.write_text("radius,lower,upper\n0,67,67\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                plot.load_intervals(path)


if __name__ == "__main__":
    unittest.main()
