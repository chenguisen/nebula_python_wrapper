# Quick Start

本页作为一张速查卡，帮助你快速跑通 STL→TRI→PRI→Nebula→DET→PNG 的端到端流程，并列出关键参数与常见问题。

## 一、端到端流程（一步到位）

1) STL → TRI（含倾转与绕法线旋转）
- 入口：`source/parameters.py` → `tri_parameters.run()` → `voxel_to_mesh.run_interface()`
- 输出：`.tri`

2) ROI/能量等 → PRI（电子束输入）
- 入口：`source/parameters.py` → `pri_parameters.run()` → `sem_pri.generate_sem_pri_data()`
- 输出：`.pri`

3) TRI + PRI + MAT → DET（调用 Nebula 可执行）
- 入口：`source/run_nebula.py` → `nebula_gpu.run()`
- 输出：`.det`

4) DET → PNG（可视化）
- 入口：`source/analysis.py` → `sem_analysis()`
- 输出：`.png`

可复用脚本：
- 自动批处理：`python source/auto_run_simulation.py`
- 图像转视频 GUI：`python source/images_to_video_gui.py`

---

## 二、关键参数速览

- STL/几何
  - `sample_tilt_x / sample_tilt_y`：样品绕 X/Y 轴倾转
  - `sample_tilt_new_z`：倾转后绕样品法线方向的旋转角
  - `det_tilt_x`：探测器绕 X 轴倾转角
  - 编码（TRI）：样品 `0 -123`，探测器 `-125 -125`，环境 `-122/-127`

- PRI/电子束
  - `pixel_size`：像素尺寸（nm）
  - `energy`：能量（eV/keV 视实现）
  - `epx`：每像素电子数（Poisson 可开启）
  - `roi_x_min/x_max/y_min/y_max`：ROI 区域（像素范围）
  - `d_zmin / d_zmax`：来自 TRI 的探测器 z 范围，用于束 z 位置计算

- 可执行/材料
  - `nebula_gpu_path`：Nebula 可执行路径（Linux 示例：`source/nebula_gpu`）
  - `mat_paths_list`：材料 `.mat` 列表（以空格拼接传入）
  - 命令模板：`"nebula_gpu" "tri" "pri" material1.mat material2.mat > output.det`

- 图像转视频 GUI（images_to_video_gui.py）
  - 支持多图选择/追加、按名称/日期排序
  - 帧率、分辨率（含自定义）、宽高比（保持/拉伸）、质量（高/标准/压缩）
  - 编码器回退：HEVC(hev1) → H.264(avc1) → mp4v；自动修正偶数宽高

---

## 三、常见问题（FAQ）

- 生成视频失败或文件不可用
  - 换 .mp4 或 .avi；确认输出目录可写
  - OpenCV 不一定带 HEVC/H.264，程序会回退到 mp4v

- Nebula 可执行路径或材料文件不存在
  - 检查 `nebula_gpu_path`、`.mat` 路径；Linux 下需 `chmod +x`

- `running: 0 | detected: 0`
  - 几何/PRI/材料设置可能存在问题；脚本会终止并提示优化输入

- 超大分辨率或超长序列导出视频耗时长
  - 降低分辨率/帧率或选择“标准/压缩”；优先使用 mp4v 提升兼容性

---

## 四、建议的开发流程

- 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 可选
```

- 统一风格与检查
```bash
make format
make lint
```

- 快速运行
```bash
make gui       # 图像转视频 GUI
make sem       # SEM 分析脚本
make sim       # 自动仿真脚本
```
