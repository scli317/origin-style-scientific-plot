# Origin Style Scientific Plot

[English](README.md) | 简体中文

一个从 Excel、CSV 或 TSV 数据生成 Origin 风格科研图的 Codex 技能。默认导出 **矢量 PDF 和 600 dpi TIFF**，PNG、SVG 按需开启。

## 功能

- 默认单栏尺寸为 8.5 × 6.05 cm，可指定尺寸或读取参考 PDF 的页面尺寸。
- 衬线字体、四边框、向内主次刻度、浅灰虚线网格和紧凑图例。
- 支持多系列对比图、单系列图，以及颜色和图例布局配置。
- 提供多转速分层图的设计规则。此类布局需要代理根据具体数据编写绘图逻辑，并非通用脚本中的独立模式。
- 使用局部插值自动修正孤立尖峰。自动检测可能误判真实瞬态，应对照原始数据检查；使用 `--no-clean-spikes` 可保留原始曲线。

## 安装为 Codex 技能

将仓库克隆至技能目录：

```bash
git clone https://github.com/scli317/origin-style-scientific-plot.git ~/.agents/skills/origin-style-scientific-plot
```

保留 `SKILL.md`、`agents/` 和 `scripts/` 的目录结构。在 Codex 中使用 `$origin-style-scientific-plot` 调用。

示例提示词：

```text
$origin-style-scientific-plot 将 input.xlsx 绘制为单栏速度对比图，横轴 Time (s)，纵轴 Velocity (m/s)，导出 PDF 和 TIFF。
```

## 独立运行脚本

需要 Python 3.10 或以上版本。在仓库目录执行：

```bash
python -m pip install -r requirements.txt
python scripts/origin_style_plot.py input.xlsx --header-depth 2 --output outputs --x-label "Time (s)" --y-label "Velocity (m/s)"
```

第一列作为横轴，其余列作为数据系列。默认读取两行表头；只有一行表头时设置 `--header-depth 1`。使用 `--sheet Sheet1` 选择 Excel 工作表。

默认生成各系列图和总对比图，使用 `--no-individual` 仅导出总对比图：

```bash
python scripts/origin_style_plot.py input.csv --header-depth 1 --output outputs --no-individual --comparison-name velocity_comparison --x-label "Time (s)" --y-label "Velocity (m/s)"
```

输出文件包括 `velocity_comparison.pdf` 和 `velocity_comparison.tiff`。`--dpi` 设置 TIFF 和可选 PNG 的分辨率，默认值为 600。添加 `--export-png` 或 `--export-svg` 可额外导出相应格式。查看完整选项：

```bash
python scripts/origin_style_plot.py --help
```

## 文件说明

- `SKILL.md`：代理指令、绘图工作流和分层图设计规范。
- `agents/openai.yaml`：代理界面配置。
- `scripts/origin_style_plot.py`：通用表格时间序列绘图脚本。
- `requirements.txt`：Python 依赖。

旋转流动工况的时间与角度转换关系为 `Angle (deg) = flow-time (s) × rpm × 6`。请核对各组数据的转速与时间起点。

## 使用注意事项

字体取决于运行环境，未安装 Times New Roman 时会使用回退字体。使用导出图片前，应检查图例遮挡、坐标单位、TIFF 分辨率及曲线与原始数据的一致性。请单独保存原始数据；脚本不会覆盖输入文件。
