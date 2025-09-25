# Nebula GPU Python 封装文档

## 概述

本文档记录了如何将 `nebula_gpu`（一个用 C++ 和 CUDA 编写的程序）封装为 Python 模块，以便通过 Python 调用。

## 封装步骤

1. **创建 Python 模块**：
   - 编写了一个 Python 脚本 `nebula_wrapper.py`，封装了对 `nebula_gpu` 的调用。
   - 脚本位于 `/home/chenguisen/AISI/nebula/nebula/nebula_wrapper.py`。

2. **功能实现**：
   - 封装了命令行参数 `sem.tri`、`sem.pri`、`silicon.mat`、`pmma.mat` 为 Python 函数的输入。
   - 支持将输出重定向到文件或直接返回给 Python。

3. **文件检查**：
   - 在调用 `nebula_gpu` 前，会检查输入文件是否存在。

## 使用方法

### 安装依赖
确保系统中已安装 Python 3 和 `subprocess` 模块（Python 标准库自带）。

### 调用示例

1. **保存输出到文件**：
   ```python
   from nebula_wrapper import run_nebula_gpu

   run_nebula_gpu(
       "sem.tri",
       "sem.pri",
       "silicon.mat",
       "pmma.mat",
       "output.det"
   )
   ```

2. **直接获取输出内容**：
   ```python
   from nebula_wrapper import run_nebula_gpu

   output = run_nebula_gpu(
       "sem.tri",
       "sem.pri",
       "silicon.mat",
       "pmma.mat"
   )
   print(output)
   ```

## 注意事项

1. **文件路径**：
   - 确保输入文件的路径正确。
   - `nebula_gpu` 的可执行文件路径默认为 `build/bin/nebula_gpu`，如需修改，请更新脚本中的路径。

2. **依赖和环境**：
   - 如果 `nebula_gpu` 需要其他依赖或环境变量，请在调用前设置。

3. **错误处理**：
   - 如果输入文件不存在，会抛出 `FileNotFoundError` 异常。
   - 如果 `nebula_gpu` 执行失败，会抛出 `subprocess.CalledProcessError` 异常。

## 后续优化建议

1. **日志记录**：
   - 可以添加日志功能，记录每次调用的参数和执行结果。

2. **性能优化**：
   - 如果需要频繁调用，可以考虑使用多线程或多进程优化性能。

3. **扩展功能**：
   - 支持更多参数或动态配置 `nebula_gpu` 的选项。