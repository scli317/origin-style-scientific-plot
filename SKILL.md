---
name: origin-style-scientific-plot
description: Generate publication-ready Origin-style scientific plots from Excel or CSV data. Use when asked to make research figures, journal single-column plots, mesh/time-series comparisons, layered multi-speed combined plots, template-matched plots from a reference PDF/image, inspect and correct obvious isolated spike outliers before plotting, or export vector PDF and 600 dpi TIFF outputs with optional PNG.
---

# Origin Style Scientific Plot

## Workflow

1. Inspect the source data before plotting. For Excel files, list sheets and read enough rows to identify header depth, x-axis column, series columns, units, and missing values.
2. Inspect each numeric series for obvious isolated spike outliers before plotting. Correct only locally inconsistent, non-physical single-point or very-short spike artifacts; replace them by local linear interpolation. Do not smooth the whole curve, remove broad physical transients, or alter data trends.
3. If a reference PDF or image is provided, extract or infer its physical size first. Use the reference dimensions unless the user gives a target size. For journal single-column figures, default to 8.5 cm width.
4. Plot with a clean Origin-like publication style: boxed axes, inward major/minor ticks on all four sides, restrained line widths, readable legends, embedded vector fonts, and no decorative background.
5. When matching a reference image like the slurry-concentration time-series example, reproduce the visible style: Times New Roman-style serif text, black boxed axes, top/right ticks, light gray dashed major grid lines behind the data, compact white legend box with black border, and legend placed at the upper right.
6. For six concentration-like series, use a two-row/three-column legend at the upper right inside the axes when it does not cover curves; otherwise keep the legend at the upper right but move it just outside the axes or expand the axis range.
7. When the legend is placed at the upper right inside the axes, reserve visible vertical space above the curve envelope. If the curve body is close to the top boundary or overlaps the legend, increase the y-axis upper limit with asymmetric top padding before moving the legend. Use enough headroom that the legend sits over blank plotting space, not over data.
8. Export vector PDF and 600 dpi TIFF by default. Generate PNG only when the user requests it. Do not export SVG unless the user explicitly asks for SVG.
9. Visually inspect the exported PDF or TIFF. Check the TIFF resolution and pixel dimensions. If PNG is requested, verify its dpi metadata and dimensions too. Report how many spike points were corrected and save a cleaned-data summary when practical.

## Layered Multi-Speed Combined Plot Mode

Use this mode when the user asks to combine several speed-specific figures/data groups into one image, especially with wording such as "分层合并图", "多转速合到一张图", "四张图片合成一张", "右侧方框标注转速", or "喷口流量颜色图例".

Preferred design:

1. Use one shared x-axis, usually `Angle (deg)` for TBM rotating-flow cases. If source Fluent `.out` files contain `flow-time`, convert to angle with `Angle = flow-time × rpm × 6`.
2. Overlay all speed groups on a single y-axis when the speed groups are naturally stratified. Do not normalize or offset curves unless the user explicitly asks for artificial offsets.
3. Encode nozzle flow rate by color, using the standard order:
   - `800 m³/h`: black
   - `900 m³/h`: red
   - `1000 m³/h`: blue
   - `1200 m³/h`: green
4. Label speed groups with individual white square boxes, black borders, and text such as `0.2 rpm`, `0.4 rpm`, `0.6 rpm`, and `0.8 rpm`. Place these boxes just outside the right axis at the vertical center of each speed layer when possible, so they do not cover curves.
5. Place the `Nozzle flow rate` legend inside the upper-right of the plotting frame when there is enough blank headroom. Use two rows and two columns for the four flow-rate entries. If the legend overlaps curves, increase the y-axis upper limit first; if overlap remains, move the legend outside.
6. Keep the y-axis label tied to the monitored quantity, for example `Mean radial velocity at radial-14 (m/s)` or `Average velocity at flash1 (m/s)`.
7. Preserve the Origin-like style: Times New Roman-style serif font, boxed axes, inward ticks on all sides, and a light gray dashed major grid. Export vector PDF and 600 dpi TIFF by default; provide PNG only when requested.
8. Save the cleaned plotting data and a correction log when spike removal is applied.

Example user prompt to trigger this mode:

```text
[$origin-style-scientific-plot] 对 D:\...\flash1-随喷口流量变化 的数据绘制分层合并图，横坐标为角度，同一喷口流量用同一颜色，右侧方框标注转速，Nozzle flow rate 图例放在框内右上角并采用两行两列。
```

## Script

Use `scripts/origin_style_plot.py` for common spreadsheet time-series plots.

Typical command:

```bash
python scripts/origin_style_plot.py input.xlsx --output outputs_8p5cm --width-cm 8.5 --height-cm 6.05 --x-label "Time (s)" --y-label "Velocity (m/s)"
```

Template-matched command for a reference-image time-series plot:

```bash
python scripts/origin_style_plot.py input.xlsx --output outputs_reference_style --sheet 0 --header-depth 2 --x-label "Time (s)" --y-label "Area-averaged radial velocity (m/s)" --line-colors "#000000" "#ff0000" "#1f77b4" "#2ca02c" "#9467bd" "#ff7f0e" --line-width 0.9 --grid-style dashed --legend-frame --legend-ncol 3 --no-legend-title --legend-loc "upper right" --comparison-name radial_velocity_reference_style --no-individual
```

Useful options:

- `--sheet Sheet1` selects an Excel sheet.
- `--header-depth 2` reads two header rows, useful when the first row contains series names and the second row contains variable names.
- `--series 582933 1070397 1528430` selects specific series by top-level header or column label.
- `--comparison-name velocity_mesh_comparison` sets the combined-plot filename stem.
- `--reference-pdf figure15.pdf` reads the first-page MediaBox/CropBox and uses that physical width and height.
- `--no-individual` skips one-figure-per-series output.
- `--no-grid` disables the default light gray dashed major grid.
- `--grid-style dashed` keeps the reference-image grid style.
- `--legend-frame` draws a white, black-bordered legend box; this is the default reference-image style.
- `--no-legend-frame` disables the legend frame only when a frameless legend is required.
- `--legend-ncol 3` forces a three-column legend, useful for six series such as `5%`, `7%`, `9%`, `11%`, `13%`, and `15%`.
- `--no-legend-title` removes the legend title; otherwise `--legend-title "Mesh count"` or similar labels the legend.
- `--line-colors "#000000" "#ff0000" "#1f77b4" "#2ca02c" "#9467bd" "#ff7f0e"` controls series colors in the preferred six-series order: black, red, blue, green, purple, orange.
- `--x-label "Time (s)" --y-label "Velocity (m/s)"` or equivalent must include units when the user asks for labeled axes.
- `--no-clean-spikes` disables default isolated-spike correction when the user explicitly wants raw curves.
- `--export-png` adds 600 dpi PNG output when requested.
- `--export-svg` adds SVG output when SVG is explicitly required.

## Style Defaults

- Use Times New Roman-style serif text when available, with fallbacks to `Arial`, `Microsoft YaHei`, `SimHei`, and `DejaVu Sans`.
- Use 8.5 cm width and approximately 6.0 cm height for single-column figures.
- If a reference PDF is provided, prefer its first-page physical size. A common single-column template is about 8.5 cm by 6.05 cm.
- Use light gray dashed major grid lines by default for Origin-like time-series figures. Keep grid lines behind the data, lighter than the axes, and avoid dense minor-grid clutter.
- Use black boxed axes with inward major and minor ticks on the bottom, top, left, and right sides.
- Use line-only curves for dense time series unless markers are explicitly requested. Prefer a line width of about 0.85-0.95 pt.
- Use the default six-series color order from the reference image: black, red, blue, green, purple, orange.
- Use a compact framed legend by default: white background, black border, no rounded corners, no title unless the user asks for a categorical title. Place it at the upper right. For many short labels, use multiple columns, e.g. three columns for six labels, to reduce vertical obstruction.
- Before finalizing a figure, visually check that the upper-right legend does not cover important curve features. If it overlaps data, first expand the y-axis upper limit with asymmetric top padding so the curve body sits lower in the plotting area; if overlap remains, keep the legend at the upper right but move it just outside the axes.
- Use `pdf.fonttype = 42`, `ps.fonttype = 42`, and `svg.fonttype = none` so vector text remains editable when SVG is requested.
- Preserve raw data except for obvious isolated spike artifacts. For spike correction, report how many points were replaced and save a cleaned-data summary when practical.

## Verification

After plotting, inspect the exported PDF and TIFF visually and check the TIFF resolution. If PNG output was requested, run a compact check similar to:

```bash
python - <<'PY'
from pathlib import Path
from PIL import Image
for p in Path("outputs_8p5cm").glob("*.tif*"):
    im = Image.open(p)
    print(p.name, im.size, im.info.get("dpi"))
PY
```

If the shell is PowerShell, use an equivalent here-string form instead of Bash heredoc syntax.
