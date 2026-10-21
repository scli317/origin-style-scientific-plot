# Origin Style Scientific Plot

English | [简体中文](README.zh-CN.md)

A Codex skill for creating Origin-style scientific plots from Excel, CSV, or TSV data. Exports **vector PDF and 600 dpi TIFF by default**, with optional PNG and SVG output.

## Features

- Single-column figures at 8.5 × 6.05 cm by default, with configurable dimensions or sizing from a reference PDF.
- Serif typography, boxed axes, inward major and minor ticks, light gray dashed grids, and compact legends.
- Combined comparisons and individual series plots, with configurable colors and legend layouts.
- Design guidance for layered plots comparing multiple rotational speeds. These layouts require task-specific plotting logic from the agent; they are not a dedicated mode in the general-purpose script.
- Automatic correction of isolated spike artifacts using local interpolation. Detection can flag genuine transients, so review corrections against the original data. Use `--no-clean-spikes` to preserve raw curves.

## Install as a Codex Skill

Clone this repository into your skills directory:

```bash
git clone https://github.com/scli317/origin-style-scientific-plot.git ~/.agents/skills/origin-style-scientific-plot
```

Keep `SKILL.md`, `agents/`, and `scripts/` together. Invoke the skill in Codex with `$origin-style-scientific-plot`.

Example prompt:

```text
$origin-style-scientific-plot Create a single-column velocity comparison from input.xlsx. Label the axes Time (s) and Velocity (m/s), and export PDF and TIFF.
```

## Run the Script Directly

Requires Python 3.10 or later. Run these commands from the repository directory:

```bash
python -m pip install -r requirements.txt
python scripts/origin_style_plot.py input.xlsx --header-depth 2 --output outputs --x-label "Time (s)" --y-label "Velocity (m/s)"
```

The first column supplies x-axis values; subsequent columns supply the data series. Two header rows are read by default. For a single header row, use `--header-depth 1`. Select an Excel worksheet with `--sheet Sheet1`.

By default, the script creates individual series plots and a combined comparison. Use `--no-individual` to export only the comparison:

```bash
python scripts/origin_style_plot.py input.csv --header-depth 1 --output outputs --no-individual --comparison-name velocity_comparison --x-label "Time (s)" --y-label "Velocity (m/s)"
```

This produces `velocity_comparison.pdf` and `velocity_comparison.tiff`. The `--dpi` option sets the TIFF and optional PNG resolution; the default is 600. Add `--export-png` or `--export-svg` to export those formats as well. For all available options:

```bash
python scripts/origin_style_plot.py --help
```

## Repository Contents

- `SKILL.md`: agent instructions, plotting workflow, and layered-plot design rules.
- `agents/openai.yaml`: agent interface configuration.
- `scripts/origin_style_plot.py`: general-purpose spreadsheet time-series plotting script.
- `requirements.txt`: Python dependencies.

For rotating-flow cases, convert time to angle using `Angle (deg) = flow-time (s) × rpm × 6`. Check the rotational speed and time origin for each dataset.

## Practical Notes

Font availability depends on the environment. Fallback fonts are used if Times New Roman is unavailable. Before using exported figures, check legend placement, axis units, TIFF resolution, and agreement with the original data. Keep the raw data separately; the script does not overwrite input files.
