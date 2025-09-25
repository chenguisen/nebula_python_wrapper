# cstool 模块导入问题解决文档

## 问题描述

在尝试运行 `cstool` 命令时，遇到以下错误：

```
ModuleNotFoundError: No module named 'cstool.apps'
```

这个错误表明 Python 无法找到 `cstool.apps` 模块，这是由于包的目录结构与 `setup.py` 中定义的包结构不匹配导致的。

## 问题分析

1. 在 `setup.py` 中，`cstool.apps` 被定义为从 `apps` 目录导入：
   ```python
   package_dir = {
       'cstool': 'cstool',
       'cstool.apps': 'apps'
   }
   ```

2. 但实际的目录结构中，`apps` 目录与 `cstool` 目录是平级的，而不是在 `cstool` 目录内。

3. 这导致 Python 在导入 `cstool.apps` 时无法找到正确的模块路径。

## 解决方案

我们采取了以下步骤来解决这个问题：

1. 修改 `setup.py` 中的 `package_dir` 配置，将 `'cstool.apps'` 映射到 `'cstool/apps'`：
   ```python
   package_dir = {
       'cstool': 'cstool',
       'cstool.apps': 'cstool/apps'
   }
   ```

2. 创建正确的目录结构，将 `apps` 目录下的文件复制到 `cstool/apps` 目录下：
   ```bash
   mkdir -p /home/chenguisen/AISI/nebula/cstool/cstool/apps
   cp /home/chenguisen/AISI/nebula/cstool/apps/__init__.py /home/chenguisen/AISI/nebula/cstool/apps/cstool.py /home/chenguisen/AISI/nebula/cstool/cstool/apps/
   ```

3. 重新安装 `cstool` 包：
   ```bash
   cd /home/chenguisen/AISI/nebula && pip install -e ./cstool
   ```

## 验证

修复后，`cstool --help` 命令可以正常运行，输出帮助信息，表明问题已解决。

## 建议

为了避免类似问题，建议在未来的开发中：

1. 确保包的目录结构与 `setup.py` 中定义的包结构一致
2. 使用标准的 Python 包结构，将子包放在父包目录下
3. 在修改包结构时，同步更新 `setup.py` 中的配置

## 日期

修复日期：2025年8月12日