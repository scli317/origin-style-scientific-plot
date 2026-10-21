from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import AutoMinorLocator


CM_TO_INCH = 1 / 2.54


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Origin-style scientific plots from spreadsheet data.")
    parser.add_argument("input", type=Path, help="Input .xlsx, .xls, .csv, or .tsv file.")
    parser.add_argument("--sheet", default=0, help="Excel sheet name or index. Ignored for CSV/TSV.")
    parser.add_argument("--header-depth", type=int, default=2, choices=[1, 2], help="Number of header rows to read.")
    parser.add_argument("--output", type=Path, default=Path("outputs_8p5cm"), help="Output directory.")
    parser.add_argument("--width-cm", type=float, default=8.5, help="Figure width in centimeters.")
    parser.add_argument("--height-cm", type=float, default=6.05, help="Figure height in centimeters.")
    parser.add_argument("--reference-pdf", type=Path, help="Optional reference PDF. Its first-page size overrides width/height.")
    parser.add_argument("--dpi", type=int, default=600, help="DPI for TIFF and optional PNG exports.")
    parser.add_argument("--x-label", default="Time", help="X-axis label.")
    parser.add_argument("--y-label", default="Velocity", help="Y-axis label.")
    parser.add_argument("--series", nargs="*", help="Optional series names to include.")
    parser.add_argument("--line-colors", nargs="*", help="Optional colors for series, for example #000000 #ff3333 #1f77ff.")
    parser.add_argument("--line-width", type=float, default=0.9, help="Series line width.")
    parser.add_argument("--comparison-name", default="comparison", help="Filename stem for the combined plot.")
    parser.add_argument("--no-individual", action="store_true", help="Skip individual series plots.")
    parser.add_argument("--grid", dest="grid", action="store_true", default=True, help="Enable light major grid lines.")
    parser.add_argument("--no-grid", dest="grid", action="store_false", help="Disable grid lines.")
    parser.add_argument("--grid-style", choices=["solid", "dashed"], default="dashed", help="Grid line style.")
    parser.add_argument("--legend-frame", dest="legend_frame", action="store_true", default=True, help="Draw a white legend box with black border.")
    parser.add_argument("--no-legend-frame", dest="legend_frame", action="store_false", help="Disable the legend frame.")
    parser.add_argument("--legend-title", default="", help="Legend title. Use an empty string for no title.")
    parser.add_argument("--no-legend-title", action="store_true", help="Remove the legend title.")
    parser.add_argument("--legend-loc", default="upper right", help="Matplotlib legend location.")
    parser.add_argument("--legend-ncol", type=int, default=0, help="Legend column count. Use 0 to auto-select.")
    parser.add_argument("--no-clean-spikes", action="store_true", help="Disable default isolated-spike correction.")
    parser.add_argument("--export-png", action="store_true", help="Also export a raster PNG at --dpi. Default outputs are PDF and TIFF.")
    parser.add_argument("--export-svg", action="store_true", help="Also export SVG.")
    return parser.parse_args()


def configure_style(dpi: int) -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Arial", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "figure.dpi": 150,
            "savefig.dpi": dpi,
            "savefig.pad_inches": 0.02,
            "axes.linewidth": 0.85,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7,
            "legend.title_fontsize": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def read_table(path: Path, sheet: str | int, header_depth: int) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        sheet_arg: str | int = int(sheet) if isinstance(sheet, str) and sheet.isdigit() else sheet
        return pd.read_excel(path, sheet_name=sheet_arg, header=list(range(header_depth)))
    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    header = list(range(header_depth)) if header_depth == 2 else 0
    return pd.read_csv(path, sep=sep, header=header)


def label_for_column(col: object) -> str:
    if isinstance(col, tuple):
        primary = col[0]
        return str(int(primary)) if isinstance(primary, float) and primary.is_integer() else str(primary)
    return str(col)


def select_series(df: pd.DataFrame, names: Iterable[str] | None) -> dict[str, pd.Series]:
    requested = set(names or [])
    out: dict[str, pd.Series] = {}
    for col in df.columns[1:]:
        label = label_for_column(col)
        if requested and label not in requested:
            continue
        out[label] = pd.to_numeric(df[col], errors="coerce")
    return out


def reference_pdf_size_cm(path: Path) -> tuple[float, float]:
    data = path.read_bytes()
    match = re.search(rb"/(?:CropBox|MediaBox)\s*\[([^\]]+)\]", data)
    if not match:
        raise ValueError(f"Could not find PDF page box in {path}")
    nums = [float(x) for x in match.group(1).split()]
    if len(nums) != 4:
        raise ValueError(f"Unexpected PDF page box in {path}: {match.group(1)!r}")
    width_pt = abs(nums[2] - nums[0])
    height_pt = abs(nums[3] - nums[1])
    return width_pt / 72 * 2.54, height_pt / 72 * 2.54


def polish_axes(ax: plt.Axes, grid: bool, grid_style: str) -> None:
    ax.tick_params(which="major", direction="in", length=3.0, width=0.8, top=True, right=True, pad=2)
    ax.tick_params(which="minor", direction="in", length=1.8, width=0.65, top=True, right=True)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    if grid:
        linestyle = (0, (1.2, 2.2)) if grid_style == "dashed" else "-"
        ax.grid(True, which="major", color="#D9D9D9", linestyle=linestyle, linewidth=0.45, alpha=0.9)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)


def clean_isolated_spikes(values: pd.Series, window: int = 9, threshold: float = 6.0) -> tuple[pd.Series, int]:
    """Replace obvious isolated spikes by linear interpolation over neighboring valid points."""
    s = pd.to_numeric(values, errors="coerce").astype(float).copy()
    if s.dropna().size < max(window, 7):
        return s, 0
    if window % 2 == 0:
        window += 1
    local = s.rolling(window=window, center=True, min_periods=max(3, window // 2)).median()
    resid = (s - local).abs()
    mad = resid.rolling(window=window, center=True, min_periods=max(3, window // 2)).median()
    global_scale = float((s - s.median()).abs().median())
    fallback = global_scale if global_scale > 0 else float(resid.median())
    if not fallback or pd.isna(fallback):
        fallback = 1e-12
    scale = mad.fillna(fallback).clip(lower=fallback * 0.25)
    candidates = resid > (threshold * 1.4826 * scale)
    # Keep only isolated or two-point artifacts; avoid removing sustained physical changes.
    isolated = candidates & ~candidates.shift(1, fill_value=False) & ~candidates.shift(-1, fill_value=False)
    two_point = candidates & (
        (candidates.shift(1, fill_value=False) & ~candidates.shift(2, fill_value=False) & ~candidates.shift(-1, fill_value=False))
        | (candidates.shift(-1, fill_value=False) & ~candidates.shift(1, fill_value=False) & ~candidates.shift(-2, fill_value=False))
    )
    mask = (isolated | two_point) & s.notna()
    corrected = s.mask(mask).interpolate(method="linear", limit_direction="both")
    return corrected, int(mask.sum())


def save_figure(fig: plt.Figure, output_dir: Path, stem: str, export_png: bool = False, export_svg: bool = False) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    suffixes = ["pdf", "tiff"]
    if export_png:
        suffixes.append("png")
    if export_svg:
        suffixes.append("svg")
    for suffix in suffixes:
        fig.savefig(output_dir / f"{stem}.{suffix}", bbox_inches=None)


def main() -> None:
    args = parse_args()
    configure_style(args.dpi)
    if args.reference_pdf:
        args.width_cm, args.height_cm = reference_pdf_size_cm(args.reference_pdf)
    df = read_table(args.input, args.sheet, args.header_depth)
    time = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    series = select_series(df, args.series)
    if not series:
        raise SystemExit("No numeric series found after the first column.")
    if not args.no_clean_spikes:
        cleaned: dict[str, pd.Series] = {}
        total_spikes = 0
        for name, values in series.items():
            corrected, count = clean_isolated_spikes(values)
            cleaned[name] = corrected
            total_spikes += count
        series = cleaned
        if total_spikes:
            print(f"Corrected isolated spike points: {total_spikes}")

    colors = args.line_colors or ["#000000", "#FF0000", "#1F77B4", "#2CA02C", "#9467BD", "#FF7F0E"]
    y_min = min(s.min() for s in series.values())
    y_max = max(s.max() for s in series.values())
    y_span = y_max - y_min
    y_lower_pad = y_span * 0.08 if y_span > 0 else 1.0
    y_upper_pad = y_span * 0.28 if y_span > 0 else 1.0
    figsize = (args.width_cm * CM_TO_INCH, args.height_cm * CM_TO_INCH)

    if not args.no_individual:
        for idx, (name, values) in enumerate(series.items()):
            fig, ax = plt.subplots(figsize=figsize)
            ax.plot(time, values, color=colors[idx % len(colors)], linewidth=args.line_width, label=name)
            ax.set_xlabel(args.x_label)
            ax.set_ylabel(args.y_label)
            ax.set_xlim(time.min(), time.max())
            ax.set_ylim(y_min - y_lower_pad, y_max + y_upper_pad)
            polish_axes(ax, args.grid, args.grid_style)
            legend_ncol = args.legend_ncol if args.legend_ncol > 0 else 1
            legend = ax.legend(
                frameon=args.legend_frame,
                loc=args.legend_loc,
                ncol=legend_ncol,
                fancybox=False,
                framealpha=1.0,
                edgecolor="black",
                facecolor="white",
                borderpad=0.25,
                handlelength=1.8,
                handletextpad=0.55,
                labelspacing=0.25,
                columnspacing=0.8,
            )
            if args.legend_frame:
                legend.get_frame().set_linewidth(0.55)
            fig.tight_layout(pad=0.35)
            save_figure(fig, args.output, f"{args.y_label.lower()}_{name}".replace(" ", "_"), args.export_png, args.export_svg)
            plt.close(fig)

    fig, ax = plt.subplots(figsize=figsize)
    for idx, (name, values) in enumerate(series.items()):
        ax.plot(time, values, color=colors[idx % len(colors)], linewidth=args.line_width, label=name)
    ax.set_xlabel(args.x_label)
    ax.set_ylabel(args.y_label)
    ax.set_xlim(time.min(), time.max())
    ax.set_ylim(y_min - y_lower_pad, y_max + y_upper_pad)
    polish_axes(ax, args.grid, args.grid_style)
    legend_ncol = args.legend_ncol if args.legend_ncol > 0 else (3 if len(series) >= 5 else 1)
    legend = ax.legend(
        title=None if args.no_legend_title else (args.legend_title or None),
        frameon=args.legend_frame,
        loc=args.legend_loc,
        ncol=legend_ncol,
        fancybox=False,
        framealpha=1.0,
        edgecolor="black",
        facecolor="white",
        borderpad=0.25,
        handlelength=1.8,
        handletextpad=0.55,
        labelspacing=0.25,
        columnspacing=0.8,
    )
    if args.legend_frame:
        legend.get_frame().set_linewidth(0.55)
    fig.tight_layout(pad=0.35)
    save_figure(fig, args.output, args.comparison_name, args.export_png, args.export_svg)
    plt.close(fig)


if __name__ == "__main__":
    main()
