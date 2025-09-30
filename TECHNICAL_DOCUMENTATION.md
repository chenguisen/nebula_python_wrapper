# Nebula Python Wrapper 技术文档

## 核心算法与实现细节

本文档详细描述了 Nebula Python Wrapper 项目中使用的核心算法和实现细节，为开发者和研究人员提供深入理解项目内部工作机制的参考。

## 1. SEM 电子束数据生成

### 1.1 算法原理

`sem_pri.py` 中的 `generate_sem_pri_data` 函数实现了扫描电子显微镜(SEM)电子束数据的生成。该算法基于以下物理和数学模型：

#### 电子束分布模型

- **空间分布**：使用高斯分布模拟电子束斑点的空间分布，其中 `sigma` 参数控制束斑大小
- **能量分布**：所有电子具有相同的初始能量，由 `energy` 参数指定
- **方向分布**：电子初始方向由 `dx`、`dy`、`dz` 参数指定，通常设置为 (0, 0, -1) 表示沿 z 轴负方向

#### 电子数量模型

- **确定性模型**：每个像素具有固定数量的电子，由 `epx` 参数指定
- **随机模型**：使用泊松分布模拟电子数量的随机性，平均值为 `epx`，更接近真实电子束的物理特性

### 1.2 数据结构

电子数据使用以下 NumPy 结构存储：

```python
electron_dtype = np.dtype([
    ('x',  '=f'), ('y',  '=f'), ('z',  '=f'),  # 位置
## 1. SEM 电子束数据生成 (更新)
    ('E',  '=f'),                              # 能量
    ('px', '=i'), ('py', '=i')                 # 像素索引
])
```

### 1.3 优化策略

为了处理大量电子数据，算法采用了以下优化策略：

1. **批处理**：将大量电子分批处理，每批最多处理 10,000 个电子，减少内存占用
2. **进度报告**：每处理 10% 的像素显示一次进度，提供剩余时间估计
3. **内存估算**：在开始处理前估算所需内存和文件大小，避免内存溢出

## 2. 网格处理与变换

### 2.1 STL 到 TRI 转换

`process_stl_to_tri.py` 实现了从标准 STL 文件到项目使用的 TRI 格式的转换：

1. **STL 解析**：读取二进制或 ASCII 格式的 STL 文件，提取三角形面片数据
2. **坐标变换**：应用缩放和平移变换，将模型调整到合适的尺寸和位置
3. **TRI 格式生成**：生成包含材质信息和三角形顶点坐标的 TRI 文件

### 2.2 网格旋转算法

`rotate_cylinder.py` 和 `generate_cylinder_mesh.py` 中实现了网格旋转算法：

```python
# 旋转矩阵计算
tilt_x_rad = math.radians(tilt_x)
cos_tx = math.cos(tilt_x_rad)
sin_tx = math.sin(tilt_x_rad)

# 应用旋转变换
y_r = y * cos_tx - z * sin_tx
z_r = y * sin_tx + z * cos_tx
```

这种旋转实现了绕 x 轴的旋转变换，用于模拟样品或探测器的倾斜。

### 2.3 体素到网格转换

`voxel_to_mesh.py` 中的 `run_interface` 函数实现了体素数据到三角形网格的转换：

1. **体素数据加载**：从 NumPy 数组或其他格式加载体素数据
2. **表面提取**：使用 Marching Cubes 或类似算法提取体素数据的表面
3. **网格简化**：根据需要简化网格，减少三角形数量
4. **网格平滑**：应用平滑算法改善网格质量
5. **坐标变换**：应用旋转、缩放等变换，调整网格位置和方向

## 3. 探测器模拟

### 3.1 探测器几何模型

探测器使用三角形网格表示，其位置和方向可以通过以下参数调整：

- **探测器倾转角**：通常为电子束成像时的 76.8 度或离子束成像时的 0 度、55 度等
```python
def run_interface(
                voxel_path,              # STL/体素数据路径（本项目常用 STL）
                mesh_path,               # 输出目录（生成 .tri 文件）
                final_side=1000,         # 目标尺寸（边长）；STL 流程中以 bbox 最大边为基准
                scale=10,                # 顶点坐标缩放因子（STL -> nm 便于计算）
                sample_tilt_x=0,         # 样品绕 X 轴倾转角
                sample_tilt_y=0,         # 样品绕 Y 轴倾转角
                sample_tilt_new_z=0,     # 倾转后绕样品法线方向的旋转角（由 rotation_matrix 计算）
                det_tilt_x=0,            # 探测器绕 X 轴倾转角（用于探测器面片）
                pad_scale=1.0,           # 体素流程使用（STL 流程忽略）
                length=64,               # 体素流程使用（STL 流程忽略）
                reverse=False            # 体素流程使用（STL 流程忽略）
                ):
```

说明：STL 流程中读取三角网格（trimesh），按 `scale` 放大并以 bbox 居中；随后应用倾转与绕法线旋转矩阵 `R`（见 `rotation_matrix.py`），再写出 TRI。函数返回：`v, faces, d_zmin, d_zmax, tri_file_path, R`，其中 `d_zmin/d_zmax` 来源于探测器三角形的 z 范围，用于生成 .pri 时确定电子束 z 位置。

附加：TRI 生成与材料编码约定（节选）
- 样品三角形行：`0 -123 x y z x1 y1 z1 x2 y2 z2`
- 探测器三角形行：`-125 -125 ...`（36 边近似圆，支持 `det_tilt_x` 旋转并上移 z+=34，最终统一转纳米）
- 环境封闭面：`-122 -122`（墙）、`-127 -127`（底面）

Nebula 可执行调用与进度监控（run_nebula.py 摘要）
- `nebula_gpu.run()` 使用 `subprocess.Popen(..., shell=True)` 执行完整命令（含重定向），并监听 stderr：
    - 检测 `running: 0 | detected: 0` 时终止进程并提示优化输入
    - 检测到 `Progress 100.00%` 后等待 20 秒仍未退出则主动终止，随后继续展示结果
- 结果展示通过 `analysis.sem_analysis` 将 `.det` 转图并保存
- **探测器位置**：相对于样品的位置，通常放置在样品上方

### 3.2 电子-探测器相互作用

当模拟的电子与探测器相交时，会记录以下信息：

- 电子的能量
- 电子的入射角度
- 相交点的位置
- 对应的原始像素坐标

这些信息被用于生成最终的模拟图像。

## 4. 图形用户界面实现

### 4.1 界面架构

`nebula_gui.py` 使用 PyQt6 实现了图形用户界面，采用以下架构：

1. **主窗口**：`NebulaGUI` 类继承自 `QMainWindow`，作为应用程序的主窗口
2. **选项卡界面**：使用 `QTabWidget` 创建多个功能选项卡
3. **参数配置区**：使用各种 Qt 控件（如 `QLineEdit`、`QSpinBox` 等）收集用户输入
4. **操作按钮**：提供执行、取消等操作的按钮
5. **输出显示区**：使用 `QTextEdit` 或 `QPlainTextEdit` 显示操作结果和日志

### 4.2 多线程处理

为了避免界面在执行耗时操作时冻结，GUI 使用 Qt 的多线程机制：

```python
class WorkerThread(QThread):
    finished = pyqtSignal(object)
    progress = pyqtSignal(int)
    
    def __init__(self, function, args):
        super().__init__()
        self.function = function
        self.args = args
        
    def run(self):
        result = self.function(*self.args)
        self.finished.emit(result)
```

### 4.3 设置持久化

使用 `QSettings` 保存和加载用户设置，确保用户的配置在应用程序重启后仍然有效：

```python
settings = QSettings("NebulaGPU", "NebulaGUI")
settings.setValue("nebula_gpu_path", path)
```

## 5. 离子束和电子束成像模式

### 5.1 离子束成像模式

离子束成像模式的特点：

- 探测器倾转角通常为 55 度或 52 度
- 离子束发射方向相对探测器平面垂直
- 样品倾转角通常与探测器倾转角相同，使样品表面与离子束方向垂直

在代码中的实现：

```python
if electron_ion_um["ion_beam"] == beam_type:
    sample_tilt_x = 55    # 样品倾转角
```

### 5.2 电子束成像模式

电子束成像模式的特点：

- 探测器倾转角为 76.8 度
- 电子束入射方向固定沿 z 轴方向（倾转角为 0 度）
- 样品可以任意倾转，通常为 0 度

在代码中的实现：

```python
elif electron_ion_um["electron_beam"] == beam_type:
    sample_tilt_x = 0   # 样品倾转角,可选择任意角度
    det_tilt_x = 76.8  # 探测器倾转角
```

## 6. 文件格式规范

### 6.1 TRI 文件格式

TRI 文件是一种文本格式，每行描述一个三角形面片：

```
material1 material2 x y z x1 y1 z1 x2 y2 z2
```

其中：
- `material1`, `material2`: 三角形两侧的材质标识符
- `x`, `y`, `z`: 第一个顶点的坐标
- `x1`, `y1`, `z1`: 第二个顶点的坐标
- `x2`, `y2`, `z2`: 第三个顶点的坐标

### 6.2 PRI 文件格式

PRI 文件是一种二进制格式，存储电子束数据，每个电子记录包含：

- 位置 (x, y, z)：电子的三维坐标
- 方向 (dx, dy, dz)：电子的运动方向向量
- 能量 (E)：电子的能量，单位为 eV
- 像素索引 (px, py)：对应的像素坐标

### 6.3 DET 文件格式

DET 文件存储探测器捕获的电子数据，包含：

- 电子的能量
- 电子的入射角度
- 相交点的位置
- 对应的原始像素坐标

## 7. 性能考量

### 7.1 内存管理

项目处理大型数据集时的内存管理策略：

1. **分批处理**：将大量数据分批处理，避免一次性加载全部数据
2. **内存预估**：在开始处理前估算所需内存，提前警告可能的内存不足
3. **临时文件**：对于超大数据集，使用临时文件存储中间结果

### 7.2 计算优化

提高计算效率的策略：

1. **向量化操作**：使用 NumPy 的向量化操作代替循环
2. **并行计算**：在适当的地方使用多线程或多进程
3. **GPU 加速**：对于支持 CUDA 的操作，使用 PyTorch 进行 GPU 加速

## 8. 扩展与定制

### 8.1 添加新的网格生成器

要添加新的网格生成器，需要：

1. 创建一个新的 Python 模块，实现网格生成算法
2. 在 `nebula_gui.py` 中添加相应的界面元素
3. 将新功能集成到现有的工作流程中

### 8.2 支持新的材料属性

要支持新的材料属性，需要：

1. 扩展 MAT 文件格式，添加新的属性字段
2. 修改相关的处理代码，考虑新属性的影响
3. 更新 GUI，允许用户设置新属性

### 8.3 自定义模拟参数

用户可以通过以下方式自定义模拟参数：

1. 通过 GUI 界面设置参数
2. 直接修改配置文件
3. 在代码中调用相关函数时传入自定义参数

## 9. 调试与故障排除

### 9.1 常见问题

1. **模块导入错误**：通常是由于包的目录结构与 `setup.py` 中定义的包结构不匹配导致的
2. **文件路径错误**：确保使用绝对路径或正确的相对路径
3. **内存不足**：处理大型数据集时可能遇到内存不足问题，尝试减小数据集大小或使用分批处理

### 9.2 调试技巧

1. **日志记录**：使用 Python 的 `logging` 模块记录关键操作和中间结果
2. **断点调试**：在 IDE 中设置断点，逐步执行代码
3. **可视化中间结果**：将中间结果保存为图像或其他可视化形式，帮助理解算法行为

## 10. 未来开发计划

### 10.1 短期计划

1. **性能优化**：提高大型数据集处理的效率
2. **用户界面改进**：增加更多可视化选项和实时预览功能
3. **文档完善**：为每个模块添加详细的 API 文档

### 10.2 长期计划

1. **支持更多材料和模拟参数**：扩展系统以支持更广泛的材料和模拟场景
2. **集成机器学习模型**：使用机器学习加速模拟过程或改进结果质量
3. **分布式计算支持**：支持在集群上运行大规模模拟

## 附录：关键函数参数说明

### generate_sem_pri_data 函数

```python
def generate_sem_pri_data(
        z: float,            # 起始z位置 (nm)
        xpx: np.ndarray,     # x像素坐标数组
        ypx: np.ndarray,     # y像素坐标数组
        energy: float = 500, # 电子束能量 (eV)
        epx: int = 1000,     # 每个像素的电子数量
        sigma: float = 1,    # 高斯光束斑点大小的标准差 (nm)
        poisson: bool = True,# 是否使用泊松散粒噪声
        dx: float = 0,       # x方向的方向向量
        dy: float = 0,       # y方向的方向向量
        dz: float = -1,      # z方向的方向向量
        file_path: str = 'sem.pri' # 输出文件路径
        ):
```

### run_interface 函数

```python
def run_interface(
        voxel_path,          # 体素数据文件路径
        mesh_path,           # 输出网格文件路径
        final_side=1000,     # 缩放参数
        sample_tilt_x=0,     # 样品倾转角
        det_tilt_x=0         # 探测器倾转角
        ):
```

## 11. 图像转视频模块（images_to_video_gui.py）

本模块提供一个基于 PyQt6 的桌面 GUI，用于选择多张图片并生成视频。核心设计点如下：

### 11.1 架构与线程模型

- UI 层：`ImageToVideoApp(QMainWindow)`
    - 图片选择与路径列表展示（支持多次添加、跨文件夹）
    - 排序（按文件名 / 修改时间）
    - 输出参数设置：帧率、分辨率（预设/自定义）、宽高比策略（保持/拉伸）、质量（高/标准/压缩）
    - 进度条与消息弹窗
- 工作线程：`VideoGeneratorThread(QThread)`
    - 输入：`image_paths: List[str]`, `output_path: str`, `fps: int`, `size: Optional[Tuple[int,int]]`, `keep_aspect: bool`, `quality: int`
    - 信号：`progress_updated(int)`, `finished(str)`, `error_occurred(str)`
    - 作用：在子线程中串行加载图片、尺寸适配、写入视频帧，避免 UI 阻塞

数据流（简要“契约”）：
- 输入：N 张图片路径，目标视频参数（fps、size、策略/质量）
- 过程：逐图读取 → 尺寸适配（保持/拉伸 + 插值）→ 写帧
- 输出：视频文件（mp4/avi），进度 0→100，错误通过信号上报

### 11.2 尺寸与插值策略

- 若未指定 size，自动使用首张图片尺寸
- `keep_aspect=True`：按比例缩放后在画布居中贴图，空白处填充黑色；`False`：直接缩放到目标尺寸
- 插值方法基于质量等级选择：
    - 高质量：`cv2.INTER_CUBIC`
    - 标准：`cv2.INTER_LINEAR`
    - 压缩：`cv2.INTER_AREA`
- 为兼容部分编码器，强制将目标宽高调整为偶数

### 11.3 编码器与回退策略

尝试顺序：
1. HEVC/H.265（fourcc: `hev1`）
2. H.264（fourcc: `avc1`）
3. MPEG-4（fourcc: `mp4v`）

若当前 OpenCV 构建不支持前两者，自动回退到 `mp4v` 确保生成成功。容器建议优先 `.mp4`，兼容性较好；如失败可尝试 `.avi`。

### 11.4 错误处理与健壮性

- I/O 错误与读取失败：对每张图片 `cv2.imread` 失败立即抛错并由 `error_occurred` 信号透传
- 写入失败：`cv2.VideoWriter.isOpened()` 多次回退后仍失败则报错
- 取消与退出：UI 关闭时若线程仍运行，调用 `stop()` 设置 `_is_running=False` 并等待线程结束
- 大批量图片：>100 张时弹出确认，避免误操作

### 11.5 性能与内存

- 单线程串行处理，适合 I/O 密集且便于保证顺序
- 内存占用主要来自当前帧，适合中等分辨率与中等数量图片
- 超大分辨率或超长序列建议：降低分辨率/质量；或将后续扩展为流式/分块读取

### 11.6 兼容性注意

- 不同平台 OpenCV 的可用编码器不同；Linux 上常见 `mp4v` 可用，HEVC/H.264 取决于构建
- 生成失败时优先检查：输出路径权限、后缀（.mp4/.avi）、分辨率是否过大

## 12. 工程化配置与开发流程

为便于统一风格与提高开发效率，项目提供以下配置与工具：

- 代码风格配置（`pyproject.toml`）
    - black：`line-length=100`
    - isort：`profile=black`
    - ruff：启用常见规则（E/F/I），忽略 `source/__pycache__`
- 开发依赖（`requirements-dev.txt`）：`ruff`, `black`, `isort`
- Makefile 常用目标：
    - `make install`：安装运行依赖
    - `make install-dev`：安装开发依赖
    - `make format`：black + isort 格式化
    - `make lint`：ruff 检查
    - `make gui`：运行图像转视频 GUI
    - `make sem`：运行 `sem-analysis.py`
    - `make sim`：运行 `auto_run_simulation.py`
- VS Code（可选，本仓库默认忽略 `.vscode/`）：
    - `tasks.json`：一键运行 GUI/脚本、安装依赖、格式化、lint
    - `extensions.json`：推荐扩展（Python、Pylance、Ruff、Black、Jupyter）

## 13. 兼容性与部署建议

- Python 版本：建议 3.9+（项目含 `__pycache__` 的 py3.13 字节码，实际运行版本需与本地环境匹配）
- OpenCV 编码器：
    - 若需 HEVC/H.264，请使用包含相应编解码支持的构建；否则使用 `.mp4` + `mp4v` 以保证成功
    - 分辨率需为偶数，过大分辨率在低配机器上可能失败
- GUI 运行环境：需具备图形桌面与 `PyQt6`；服务器环境建议后续扩展 CLI 无头模式

## 14. 测试与验证建议

- 单元测试（建议新增）：
    - 参数解析与尺寸计算：`_get_video_size`、偶数宽高修正
    - 排序功能：按名称/日期排序是否稳定
- 集成测试：
    - 用 5~10 张小图（如 640x480）生成短视频（2~3 秒）验证编码器回退逻辑
    - 生成 `.mp4` 与 `.avi`，确保至少有一种容器成功
- 压力测试（手动）：
    - 1000 张以上、1080p/4K，观察内存与耗时，指导用户参数建议
