"""Plot the four retained selected-plan intervals with native PDF graphics."""
from pathlib import Path
import argparse
import csv
import os
import tempfile

EXPECTED = [(0, 67, 67), (1, 44, 92), (3, 28, 140), (7, 4, 236)]


def load_intervals(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    data = [(int(r["radius"]), int(r["lower"]), int(r["upper"])) for r in rows]
    if data != EXPECTED:
        raise ValueError("Interval rows differ from the retained four-instance table")
    return data


def render(csv_path, output):
    data = load_intervals(csv_path)
    # Font caches stay outside the research material.
    with tempfile.TemporaryDirectory(prefix="footprintready-plot-") as cache:
        previous = os.environ.get("MPLCONFIGDIR")
        os.environ["MPLCONFIGDIR"] = cache
        try:
            import matplotlib
            matplotlib.use("pdf")
            import matplotlib.pyplot as plt
            matplotlib.rcParams.update({
                "font.family": "serif",
                "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
                "font.size": 8.5,
                "mathtext.fontset": "stix",
                "text.usetex": False,
                "pdf.fonttype": 42,
                "axes.labelsize": 8.5,
                "xtick.labelsize": 8.5,
                "ytick.labelsize": 8.5,
                "axes.linewidth": 0.55,
            })
            radius, lower, upper = zip(*data)
            fig = plt.figure(figsize=(3.5, 4.20 / 2.54))
            ax = fig.add_axes([0.17, 0.29, 0.80, 0.66])
            ax.plot(radius, upper, "s-", color="black", markersize=4,
                    linewidth=0.7, label="$U(P)$")
            ax.plot(radius, lower, "o--", color="black", markerfacecolor="white",
                    markersize=4, linewidth=0.7, label="$L(P)$")
            ax.set(xlim=(-0.3, 7.3), ylim=(-4, 260),
                   xlabel="Interval radius (cost units)", ylabel="Selected-plan cost")
            ax.set_xticks([0, 1, 3, 7])
            ax.set_yticks([0, 50, 100, 150, 200, 250])
            ax.grid(color="0.82", linestyle=":", linewidth=0.45)
            ax.tick_params(length=3, width=0.55)
            ax.legend(loc="upper left", frameon=False, fontsize=8.5,
                      borderaxespad=0.35, handlelength=2)
            output = Path(output)
            output.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output, format="pdf", metadata={
                "Creator": "Python Matplotlib", "CreationDate": None, "ModDate": None})
            plt.close(fig)
        finally:
            if previous is None:
                os.environ.pop("MPLCONFIGDIR", None)
            else:
                os.environ["MPLCONFIGDIR"] = previous
    return data


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=root / "results/interval-costs.csv")
    parser.add_argument("--out", type=Path, default=root / "figures/interval-costs.pdf")
    args = parser.parse_args()
    data = render(args.csv, args.out)
    print(f"Retained radius/lower/upper={data}; vector PDF generated.")


if __name__ == "__main__":
    main()
