# Nebula Python Wrapper 用户指南

## 简介

Nebula Python Wrapper 是一组用于运行与分析 Nebula 仿真结果的 Python 脚本与工具集。本文档将帮助你安装、配置并使用这些脚本完成扫描电子显微镜（SEM）与离子束成像相关的仿真、数据转换与可视化，同时也包含一个“图像转视频”的桌面 GUI 工具。

更新日期：2025-09-30

## 目录

1. [安装指南](#1-安装指南)
2. [快速入门](#2-快速入门)
3. [图形界面：图像转视频](#3-图形界面图像转视频)
4. [命令/脚本入口](#4-命令脚本入口)
5. [编程接口使用（示例）](#5-编程接口使用示例)
6. [常见工作流程](#6-常见工作流程)
7. [文件格式说明](#7-文件格式说明)
8. [常见问题解答](#8-常见问题解答)
9. [故障排除](#9-故障排除)
10. [高级功能](#10-高级功能)
11. [更多资料](#11-更多资料)

## 1. 安装指南

### 系统要求

- Python 3.9+（建议）
- Linux 优先支持；其他平台可按依赖情况尝试
- GPU 可选（用于加速），CPU 同样可用
- 建议 16GB 内存以上，磁盘空间 ≥ 10GB

### 安装步骤

1. 克隆仓库

   ```bash
   git clone https://github.com/chenguisen/nebula_python_wrapper.git
   cd nebula_python_wrapper
   ```

2. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

3. 可选：开发模式安装（便于后续开发）

   ```bash
   pip install -e .
   ```

4. 可选：验证环境

   ```bash
   python -V
   pip list | grep opencv
   ```

提示：本项目新增了“图像转视频”工具，依赖 opencv-python 与 PyQt6，requirements.txt 已包含。

## 2. 快速入门

### 基本概念

项目涉及的主要数据类型：

- STL：3D 模型的标准格式
- TRI：含材质标记的三角网格（Nebula 输入之一）
- PRI：电子/离子束像素扫描数据（Nebula 输入之一）
- DET：探测器输出数据（Nebula 输出）

### 快速示例

方式 A：一键跑通 SEM 仿真（推荐）

```bash
python source/auto_run_simulation.py
```

在运行前，可在脚本顶部修改以下参数：
- `mat_paths_list`：材料 .mat 文件列表
- `nebula_gpu_path`：Nebula 可执行程序路径（确保存在且可执行）
- `stl_dir`：输入 STL 所在目录
- 其他：`pixel_size`、`energy`、`epx`、倾转角与旋转列表等

方式 B：图像转视频 GUI（将多张图片合成为视频）

```bash
python source/images_to_video_gui.py
```

该 GUI 支持多选图片、排序、设置帧率/分辨率/质量，并自动适配编码器（HEVC→H.264→mp4v 回退）。

## 3. 图形界面：图像转视频

本仓库提供一个 PyQt6 桌面应用，将多张图片快速合成为 MP4/AVI 视频。

### 启动

```bash
python source/images_to_video_gui.py
```

### 功能要点

- 图片导入：选择图片/添加更多/从文件夹导入；支持 .png/.jpg/.jpeg/.bmp/.tif/.tiff
- 排序：按名称或日期
- 输出：选择目标视频文件（建议 .mp4）
- 参数：FPS、分辨率（预设或自定义）、宽高比（保持/拉伸）、质量（高/标准/压缩）
- 细节：自动将奇数宽高修正为偶数；编码器自动回退确保生成成功

提示：关于编码器兼容性、黑边/拉伸说明与常见问题，见 README 的“图像转视频 GUI”章节。

## 4. 命令/脚本入口

除了 GUI，本项目还提供若干可直接运行的脚本，适合批处理与自动化：

### 常用脚本

1) 运行 SEM 分析（按需调整脚本内部路径）

```bash
python source/sem-analysis.py
```

2) 运行完整仿真（自动生成 .tri/.pri 并调用 Nebula）

```bash
python source/auto_run_simulation.py
```

3) 使用 Makefile 快捷命令（可选）

```bash
make install       # 安装依赖
make gui           # 启动图像转视频 GUI
make sem           # 运行 sem-analysis.py
make sim           # 运行 auto_run_simulation.py
make format        # 代码格式化（black/isort）
make lint          # 代码检查（ruff）
```

注意：部分旧版文档中提到的 shell 脚本与命令（如 `run_tri_pri_generator.sh`、`nebula-sem-analysis` 控制台命令）在当前仓库中并未提供，请以上述脚本为准。

## 5. 编程接口使用（示例）

Nebula Python Wrapper 提供了 Python 编程接口，允许您在自己的脚本中使用其功能。

### 导入模块

```python
# TRI/PRI 生成与 Nebula 运行（简要示例）
from source.parameters import tri_parameters, pri_parameters
from source.run_nebula import nebula_gpu
import pathlib

stl_path = pathlib.Path('/path/to/model.stl')
mesh_path = stl_path.parent / 'mesh_out'

# 1) 生成 TRI
TRI = tri_parameters(
   stl_path=stl_path,
   mesh_path=mesh_path,
   beam_type='electron',
   sample_tilt_x=0,
   sample_tilt_y=0,
   sample_tilt_new_z=0,
   det_tilt_x=76.8,
)
v, faces, d_zmin, d_zmax, tri_file_path, R = TRI.run()

# 2) 生成 PRI（示意）
PRI = pri_parameters(
   pri_dir=str(stl_path.parent),
   pixel_size=2,
   energy=500,
   epx=500,
   sigma=1.0,
   poisson=True,
   roi_x_min=-256, roi_x_max=255,
   roi_y_min=-256, roi_y_max=255,
   d_zmin=d_zmin, d_zmax=d_zmax,
)
pri_file_path = PRI.run()

# 3) 调用 Nebula 运行
nebula_exe = pathlib.Path('source/nebula_gpu')  # 修改为你的可执行文件路径
det_out = stl_path.parent / 'output.det'
cmd = f'"{nebula_exe}" "{tri_file_path}" "{pri_file_path}" /path/to/materials/silicon.mat > "{det_out}"'

NEBULA = nebula_gpu(command=cmd, sem_simu_result=str(det_out), image_path=tri_file_path.with_suffix('.png'))
NEBULA.run()
```

### 生成 SEM 电子束数据

```python
import numpy as np
from source.sem_pri import generate_sem_pri_data

# 设置参数
z = 150                            # 起始z位置 (nm)
xpx = np.linspace(-128, 128, 512)  # x像素范围
ypx = np.linspace(-128, 128, 512)  # y像素范围
energy = 500                       # 电子束能量 (eV)
epx = 1000                         # 每个像素的电子数量

# 生成数据
generate_sem_pri_data(
    z=z,
    xpx=xpx,
    ypx=ypx,
    energy=energy,
    epx=epx,
    sigma=1.0,
    poisson=True,
    file_path='data/sem.pri'
)
```

### 处理 STL 文件

```python
from source.process_stl_to_tri import process_stl_to_tri

# 转换 STL 到 TRI
process_stl_to_tri(
    input_file='data/model.stl',
    output_file='data/model.tri',
    scale=1.0,
    translate=[0, 0, 0]
)
```

### 体素到网格转换

```python
from source.voxel_to_mesh import run_interface

# 转换体素数据到网格
v, faces, d_zmin, d_zmax = run_interface(
    voxel_path='data/voxel_data.npy',
    mesh_path='data/',
    final_side=1000,
    sample_tilt_x=0,
    det_tilt_x=76.8
)
```

## 6. 常见工作流程

### 电子束成像工作流程

1. **准备 3D 模型**（STL 格式）
2. **转换为 TRI 格式**
3. **设置样品倾转角**（通常为 0 度）
4. **设置探测器倾转角**（76.8 度）
5. **生成 PRI 文件**
6. **运行模拟**
7. **分析结果**

### 离子束成像工作流程

1. **准备 3D 模型**（STL 格式）
2. **转换为 TRI 格式**
3. **设置样品倾转角**（通常为 55 度）
4. **设置探测器倾转角**（0 度）
5. **生成 PRI 文件**
6. **运行模拟**
7. **分析结果**

### 参数优化工作流程

1. **设置基准参数**
2. **运行初始模拟**
3. **分析结果**
4. **调整参数**
5. **重新运行模拟**
6. **比较结果**
7. **重复步骤 4-6 直到获得满意结果**

## 7. 文件格式说明

### STL 文件

STL（STereoLithography）是一种表示 3D 模型的标准文件格式，可以是二进制或 ASCII 格式。

### TRI 文件

TRI 文件是一种文本格式，每行描述一个三角形面片：

```
material1 material2 x y z x1 y1 z1 x2 y2 z2
```

其中：
- `material1`, `material2`: 三角形两侧的材质标识符
- `x`, `y`, `z`: 第一个顶点的坐标
- `x1`, `y1`, `z1`: 第二个顶点的坐标
- `x2`, `y2`, `z2`: 第三个顶点的坐标

### PRI 文件

PRI 文件是一种二进制格式，存储电子束数据，每个电子记录包含：

- 位置 (x, y, z)
- 方向 (dx, dy, dz)
- 能量 (E)
- 像素索引 (px, py)

### DET 文件

DET 文件存储探测器捕获的电子数据，包含电子的能量、入射角度、相交点位置和对应的原始像素坐标。

## 8. 常见问题解答

### Q: 如何选择合适的电子束能量？

A: 电子束能量通常在 100eV 到 30keV 之间。较低的能量适合表面分析，较高的能量适合深层分析。对于大多数应用，500eV 是一个好的起点。

### Q: 如何提高模拟精度？

A: 提高模拟精度的方法：
- 增加每个像素的电子数量 (`epx` 参数)
- 减小光束斑点大小 (`sigma` 参数)
- 增加像素分辨率 (增加 `xpx` 和 `ypx` 数组的长度)

### Q: 如何处理大型模型？

A: 处理大型模型的建议：
- 使用网格简化技术减少三角形数量
- 增加系统内存
- 使用分批处理方法
- 考虑使用 GPU 加速

### Q: 电子束和离子束成像有什么区别？

A: 主要区别：
- 电子束：探测器倾转角为 76.8 度，电子束沿 z 轴方向
- 离子束：探测器倾转角为 0 度或 55 度，离子束相对探测器平面垂直

## 9. 故障排除

### 模块导入错误

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
1. 确保已安装所有依赖：`pip install -r requirements.txt`
2. 检查包的目录结构与 `setup.py` 中定义的包结构是否匹配
3. 尝试重新安装包：`pip install -e .`

### 内存不足

**问题**：`MemoryError` 或程序崩溃

**解决方案**：
1. 减小数据集大小或分辨率
2. 使用分批处理方法
3. 增加系统内存
4. 关闭其他内存密集型应用程序

### 文件路径错误

**问题**：`FileNotFoundError: No such file or directory`

**解决方案**：
1. 使用绝对路径而不是相对路径
2. 确保文件名和路径中没有特殊字符
3. 检查文件权限

### GPU 相关错误

**问题**：CUDA 相关错误

**解决方案**：
1. 确保已安装兼容的 CUDA 驱动程序
2. 检查 GPU 内存是否足够
3. 尝试降低批处理大小
4. 如果问题持续，切换到 CPU 模式

## 10. 高级功能

### 自定义材料属性

您可以通过创建自定义 MAT 文件来定义新的材料属性：

1. 创建一个文本文件，每行包含一个属性及其值
2. 保存为 `.mat` 文件
3. 在模拟中使用该文件

### 批处理模拟

对于需要运行多个模拟的情况，可以创建批处理脚本：

```bash
#!/bin/bash

# 批处理模拟示例
for energy in 100 200 500 1000; do
    echo "Running simulation with energy $energy eV"
    python source/sem_pri.py --energy $energy --output data/sem_${energy}eV.pri
    ./run_tri_pri_generator.sh data/sem_${energy}eV.pri
done
```

### 结果可视化

使用 Matplotlib 或其他可视化工具分析结果：

```python
import matplotlib.pyplot as plt
import numpy as np

# 加载结果数据
data = np.load('data/simulation_results.npy')

# 创建热图
plt.figure(figsize=(10, 8))
plt.imshow(data, cmap='viridis')
plt.colorbar(label='Electron Count')
plt.title('SEM Simulation Results')
plt.xlabel('X Pixel')
plt.ylabel('Y Pixel')
plt.savefig('data/simulation_results.png', dpi=300)
plt.show()
```

### 参数扫描

通过系统地改变参数并比较结果，可以找到最佳参数组合：

```python
import numpy as np
from source.sem_pri import generate_sem_pri_data

# 参数扫描示例
energies = [100, 200, 500, 1000]
sigmas = [0.5, 1.0, 2.0]

for energy in energies:
    for sigma in sigmas:
        print(f"Testing energy={energy}eV, sigma={sigma}nm")
        generate_sem_pri_data(
            z=150,
            xpx=np.linspace(-128, 128, 256),  # 降低分辨率以加快扫描
            ypx=np.linspace(-128, 128, 256),
            energy=energy,
            epx=500,
            sigma=sigma,
            file_path=f'data/scan_e{energy}_s{sigma}.pri'
        )
        # 运行模拟并分析结果
        # ...
```

## 11. 更多资料

- 快速上手（一页速查）：docs/QuickStart.md
- 项目结构与流程：PROJECT_DOCUMENTATION.md（含 Mermaid 流程图）
- 设计细节与技术说明：TECHNICAL_DOCUMENTATION.md

## 结语

本用户指南涵盖了 Nebula Python Wrapper 的基本使用方法和高级功能。随着您对工具的熟悉，您将能够执行更复杂的模拟和分析。如有任何问题或建议，请参考项目文档或联系开发团队。

祝您使用愉快！