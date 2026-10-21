# Origin Style Scientific Plot

从 Excel、CSV 或 TSV 数据生成 Origin 风格科研图的 Codex 技能。默认输出 **矢量 PDF 和 600 dpi TIFF**，PNG、SVG 按需开启。

## 功能

- 默认单栏尺寸 8.5 × 6.05 cm，可指定尺寸或读取参考 PDF 的页面尺寸。
- 衬线字体、四边框、向内主次刻度、浅灰虚线网格和紧凑图例。
- 支持多数据系列对比、单系列图、颜色及图例布局配置。
- 技能说明提供多转速分层图的设计规则；该模式需要代理按具体数据编写绘图逻辑，并非通用脚本中的独立命令选项。
- 可识别并插值替换孤立尖峰。自动判断不保证区分所有真实瞬态，科研使用前应核对原始数据；使用 `--no-clean-spikes` 可保留原始曲线。

## 安装为 Codex 技能

将本目录放入 `~/.agents/skills/origin-style-scientific-plot/`，保留 `SKILL.md`、`agents/` 和 `scripts/` 目录结构。在 Codex 中使用 `$origin-style-scientific-plot` 调用。

示例提示词：

```text
$origin-style-scientific-plot 将 input.xlsx 绘制为单栏速度对比图，横轴 Time (s)，纵轴 Velocity (m/s)，默认导出 PDF 和 TIFF。
```

## 独立脚本使用

需要 Python 3.10 或以上版本：

```bash
python -m pip install -r requirements.txt
python scripts/origin_style_plot.py input.xlsx --header-depth 2 --output outputs --x-label "Time (s)" --y-label "Velocity (m/s)"
```

第一列作为横轴，其余列作为数据系列。默认读取两行表头；只有一行表头时设置 `--header-depth 1`。Excel 工作表可通过 `--sheet Sheet1` 选择。

默认生成各系列图和总对比图，使用 `--no-individual` 仅保留总对比图：

```bash
python scripts/origin_style_plot.py input.csv --header-depth 1 --output outputs --no-individual --comparison-name velocity_comparison --x-label "Time (s)" --y-label "Velocity (m/s)"
```

输出包括 `velocity_comparison.pdf` 和 `velocity_comparison.tiff`。`--dpi` 可调整 TIFF 和可选 PNG 的分辨率；默认 600。添加 `--export-png` 或 `--export-svg` 可额外导出相应格式。完整选项见：

```bash
python scripts/origin_style_plot.py --help
```

## 文件说明

- `SKILL.md`：技能调用规则、绘图工作流和分层图设计规范。
- `agents/openai.yaml`：代理界面配置。
- `scripts/origin_style_plot.py`：通用表格时间序列绘图脚本。
- `requirements.txt`：脚本依赖。

分层旋转工况中，时间转换为角度的关系为 `Angle (deg) = flow-time (s) × rpm × 6`。请核对转速与数据时间基准。

## 使用说明

字体取决于运行环境，未安装 Times New Roman 时会使用回退字体。导出后应检查图例遮挡、坐标单位、TIFF 分辨率和曲线是否符合原始数据。原始数据应单独保留；脚本不会覆盖输入文件。
