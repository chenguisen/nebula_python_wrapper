# Nebula Python Wrapper 用户指南

## 简介

Nebula Python Wrapper 是一个用于分析 Nebula 模拟结果的 Python 工具集。本指南将帮助您了解如何安装、配置和使用该工具进行扫描电子显微镜(SEM)和离子束成像的模拟与分析。

## 目录

1. [安装指南](#1-安装指南)
2. [快速入门](#2-快速入门)
3. [图形用户界面使用](#3-图形用户界面使用)
4. [命令行工具使用](#4-命令行工具使用)
5. [编程接口使用](#5-编程接口使用)
6. [常见工作流程](#6-常见工作流程)
7. [文件格式说明](#7-文件格式说明)
8. [常见问题解答](#8-常见问题解答)
9. [故障排除](#9-故障排除)
10. [高级功能](#10-高级功能)

## 1. 安装指南

### 系统要求

- Python 3.6 或更高版本
- 支持 CUDA 的 GPU（可选，用于加速计算）
- 至少 8GB RAM（推荐 16GB 或更多）
- 至少 10GB 可用磁盘空间

### 安装步骤

1. **克隆仓库**

   ```bash
   git clone https://github.com/your-username/nebula_python_wrapper.git
   cd nebula_python_wrapper
   ```

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **安装包**

   ```bash
   pip install -e .
   ```

4. **验证安装**

   ```bash
   python -c "import nebula_python_wrapper; print('安装成功')"
   ```

## 2. 快速入门

### 基本概念

Nebula Python Wrapper 主要处理以下类型的数据：

- **STL 文件**：3D 模型的标准格式
- **TRI 文件**：包含材质信息的三角形网格文件
- **PRI 文件**：电子束数据文件
- **DET 文件**：探测器输出文件

### 简单示例

以下是一个简单的工作流程示例：

1. **准备 STL 模型**

   将您的 3D 模型保存为 STL 格式，并放置在 `data` 目录中。

2. **转换为 TRI 格式**

   ```bash
   python source/process_stl_to_tri.py data/your_model.stl data/your_model.tri
   ```

3. **生成 PRI 文件**

   ```bash
   python -c "from source.sem_pri import generate_sem_pri_data; import numpy as np; generate_sem_pri_data(150, np.linspace(-128, 128, 512), np.linspace(-128, 128, 512), file_path='data/sem.pri')"
   ```

4. **运行模拟**

   ```bash
   ./run_tri_pri_generator.sh
   ```

5. **查看结果**

   结果文件将保存在 `data` 目录中。

## 3. 图形用户界面使用

Nebula Python Wrapper 提供了一个基于 PyQt6 的图形用户界面，使您能够更直观地操作。

### 启动界面

```bash
python source/nebula_gui.py
```

### 界面概述

界面分为以下几个主要选项卡：

1. **Nebula GPU 参数配置**：配置 Nebula GPU 的运行参数
2. **TRI 和 PRI 生成器**：生成和处理 TRI 和 PRI 文件

### Nebula GPU 参数配置

在此选项卡中，您可以：

1. **选择 nebula_gpu 路径**：指定 nebula_gpu 可执行文件的路径
2. **选择输入文件**：
   - .tri 文件：三角形网格文件
   - .pri 文件：电子束数据文件
   - .mat 文件：材料属性文件（可多选）
3. **设置输出文件**：指定输出文件的路径
4. **配置运行参数**：设置各种模拟参数
5. **执行模拟**：点击"运行"按钮开始模拟

### TRI 和 PRI 生成器

在此选项卡中，您可以：

1. **STL 到 TRI 转换**：
   - 选择 STL 文件
   - 设置转换参数
   - 生成 TRI 文件
2. **PRI 文件生成**：
   - 设置电子束参数
   - 配置像素范围和分辨率
   - 生成 PRI 文件
3. **样品和探测器设置**：
   - 调整样品倾转角
   - 设置探测器倾转角
   - 选择成像模式（电子束或离子束）

## 4. 命令行工具使用

除了图形界面，Nebula Python Wrapper 还提供了命令行工具，适合批处理和自动化脚本。

### 可用命令

1. **SEM 分析**

   ```bash
   nebula-sem-analysis <input_file>
   ```

2. **STL 到 TRI 转换**

   ```bash
   python source/process_stl_to_tri.py <input_stl> <output_tri> [options]
   ```

   选项：
   - `--scale <value>`: 缩放因子
   - `--translate <x,y,z>`: 平移向量

3. **生成 PRI 文件**

   ```bash
   python source/sem_pri.py <output_file> [options]
   ```

   选项：
   - `--energy <value>`: 电子束能量 (eV)
   - `--epx <value>`: 每个像素的电子数量
   - `--sigma <value>`: 光束斑点大小 (nm)

4. **运行完整工作流程**

   ```bash
   ./run_tri_pri_generator.sh
   ```

## 5. 编程接口使用

Nebula Python Wrapper 提供了 Python 编程接口，允许您在自己的脚本中使用其功能。

### 导入模块

```python
# 导入 SEM 电子束数据生成模块
from source.sem_pri import generate_sem_pri_data

# 导入 STL 到 TRI 转换模块
from source.process_stl_to_tri import process_stl_to_tri

# 导入体素到网格转换模块
from source.voxel_to_mesh import run_interface
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

## 结语

本用户指南涵盖了 Nebula Python Wrapper 的基本使用方法和高级功能。随着您对工具的熟悉，您将能够执行更复杂的模拟和分析。如有任何问题或建议，请参考项目文档或联系开发团队。

祝您使用愉快！