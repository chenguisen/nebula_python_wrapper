# Nebula Python Wrapper 项目文档

## 项目概述

Nebula Python Wrapper 是一个用于分析 Nebula 模拟结果的 Python 封装工具。该项目提供了一系列工具和脚本，用于处理扫描电子显微镜(SEM)和离子束成像的模拟数据，包括网格生成、数据处理和可视化功能。

## 项目结构

```
nebula_python_wrapper/
├── data/                           # 数据文件目录
│   ├── *.stl                       # 3D模型文件
│   ├── *.tri                       # 三角形网格文件
│   ├── *.txt                       # 文本数据文件
│   ├── *.tif                       # 图像文件
│   ├── *.mat                       # 材料属性文件
│   ├── *.det                       # 探测器输出文件
│   ├── *.pri                       # 电子束数据文件
│   └── *.npy                       # NumPy数组数据文件
├── docs/                           # 文档目录
│   └── nebula_gpu_python_wrapper_doc.md  # Nebula GPU Python封装文档
├── source/                         # 源代码目录
│   ├── __init__.py                 # 包初始化文件
│   ├── generate_circular_mesh.py   # 生成圆形网格的脚本
│   ├── generate_tri_pri.py         # 生成三角形和电子束数据的脚本
│   ├── nebula_gpu                  # Nebula GPU可执行文件
│   ├── nebula_gui.py               # 图形用户界面脚本
│   ├── process_stl_to_tri.py       # STL到TRI格式转换脚本
│   ├── read_stl_to_txt.py          # STL到TXT格式转换脚本
│   ├── sem_pri.py                  # SEM电子束数据生成脚本
│   ├── sem-analysis.py             # SEM分析脚本
│   └── voxel_to_mesh.py            # 体素到网格转换脚本
├── generate_cylinder_mesh.py       # 生成圆柱体网格的脚本
├── README.md                       # 项目说明文件
├── requirements.txt                # 项目依赖列表
├── rotate_cylinder.py              # 旋转圆柱体的脚本
├── run_tri_pri_generator.sh        # 运行三角形和电子束数据生成器的脚本
├── setup.py                        # 项目安装脚本
└── troubleshooting.md              # 故障排除文档
```

## 核心功能

### 1. SEM 图像模拟

项目提供了一套完整的工具链，用于模拟扫描电子显微镜(SEM)图像：

- **电子束数据生成**：`sem_pri.py` 脚本生成包含电子束数据的 `.pri` 文件，模拟电子在样品表面的行为。
- **网格生成与处理**：提供了多种工具来生成和处理三角形网格，包括从 STL 文件转换、旋转和变换网格等。
- **探测器模拟**：模拟电子与样品相互作用后被探测器捕获的过程，生成 `.det` 文件。

### 2. 几何处理工具

- **STL 文件处理**：`process_stl_to_tri.py` 和 `read_stl_to_txt.py` 提供了 STL 文件的读取和转换功能。
- **网格生成**：`generate_circular_mesh.py` 和 `generate_cylinder_mesh.py` 用于生成特定形状的网格。
- **网格变换**：`rotate_cylinder.py` 提供了网格旋转功能，用于模拟样品在不同角度下的情况。
- **体素到网格转换**：`voxel_to_mesh.py` 实现了体素数据到三角形网格的转换。

### 3. 图形用户界面

`nebula_gui.py` 提供了一个基于 PyQt6 的图形用户界面，使用户能够：

- 配置 Nebula GPU 参数
- 生成和处理 TRI 和 PRI 文件
- 可视化模拟结果
- 调整样品和探测器的倾转角度

## 技术细节

### 电子束模拟

`sem_pri.py` 中的 `generate_sem_pri_data` 函数是电子束模拟的核心，它：

1. 生成一个包含电子位置、方向、能量和像素信息的数据结构
2. 支持泊松分布的电子数量，模拟真实电子束的散粒噪声
3. 支持高斯分布的光束斑点大小
4. 优化了内存使用，通过分批处理大量电子数据

### 网格处理

项目包含多种网格处理功能：

1. **STL 到 TRI 转换**：将标准 STL 文件转换为项目使用的 TRI 格式
2. **网格旋转**：支持按指定角度旋转网格，模拟样品倾斜
3. **探测器位置调整**：可以调整探测器的位置和角度，模拟不同的成像条件

### 离子束和电子束成像

项目支持两种主要的成像模式：

1. **离子束成像**：
   - 探测器倾转角通常为 55 度或 52 度
   - 离子束发射方向相对探测器平面垂直
   - 样品倾转角通常与探测器倾转角相同

2. **电子束成像**：
   - 探测器倾转角为 76.8 度
   - 电子束入射方向固定沿 z 轴方向（倾转角为 0 度）
   - 样品可以任意倾转

## 安装与使用

### 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 使用方法

#### 命令行工具

```bash
# 运行 SEM 分析
nebula-sem-analysis <input_file>

# 生成三角形和电子束数据
./run_tri_pri_generator.sh
```

#### 图形界面

```bash
# 启动图形用户界面
python source/nebula_gui.py
```

#### 编程接口

```python
# 生成 SEM 电子束数据
from source.sem_pri import generate_sem_pri_data

# 设置参数
z = 150                            # 起始z位置 (nm)
xpx = np.linspace(-128, 128, 512)  # x像素范围
ypx = np.linspace(-128, 128, 512)  # y像素范围
energy = 500                       # 电子束能量 (eV)
epx = 1000                         # 每个像素的电子数量

# 生成数据
generate_sem_pri_data(z, xpx, ypx, energy, epx, file_path='data/sem.pri')

# 处理 STL 文件
from source.process_stl_to_tri import process_stl_to_tri

process_stl_to_tri('data/model.stl', 'data/output.tri')
```

## 故障排除

项目包含一个 `troubleshooting.md` 文件，记录了常见问题的解决方案，特别是关于模块导入问题的解决方法。

## 依赖项

- NumPy：用于数值计算
- Matplotlib：用于数据可视化
- PyQt6：用于图形用户界面
- Torch：用于某些计算加速

## 未来发展方向

1. **性能优化**：
   - 进一步优化大型数据集的处理
   - 利用 GPU 加速更多计算过程

2. **功能扩展**：
   - 支持更多材料属性和模拟参数
   - 增加更多几何形状的网格生成工具

3. **用户界面改进**：
   - 增加实时预览功能
   - 提供更多可视化选项

4. **文档完善**：
   - 为每个模块添加详细的 API 文档
   - 提供更多使用示例和教程

## 结论

Nebula Python Wrapper 项目提供了一套完整的工具，用于扫描电子显微镜和离子束成像的模拟和分析。通过提供命令行工具、编程接口和图形用户界面，该项目满足了不同用户的需求，从研究人员到工程师都可以方便地使用这些工具进行科学研究和工程应用。