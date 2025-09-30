"""
图像转视频工具 (带GUI界面)

功能:
1. 通过GUI界面选择多张图片（支持从不同文件夹选择）
2. 设置输出视频参数（分辨率、帧率、质量等）
3. 支持高分辨率视频生成（最高支持4K/8K）
4. 支持多种视频质量选项
5. 生成高质量视频文件

依赖:
- PyQt6
- OpenCV (opencv-python)
"""
import sys
import os
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QLineEdit, QSpinBox,
                             QComboBox, QProgressBar, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class VideoGeneratorThread(QThread):
    """视频生成线程"""
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, image_paths: List[str], output_path: str, fps: int = 30,
                 size: Optional[Tuple[int, int]] = None, keep_aspect: bool = True, 
                 quality: int = 1):
        super().__init__()
        self.image_paths = image_paths
        self.output_path = output_path
        self.fps = fps
        self.size = size
        self.keep_aspect = keep_aspect
        self.quality = quality  # 0=高质量, 1=标准, 2=压缩
        self._is_running = True

    def run(self):
        try:
            # 确保输出目录存在
            output_dir = Path(self.output_path).parent
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            # 获取第一张图片的尺寸(如果未指定尺寸)
            if self.size is None:
                first_image = cv2.imread(self.image_paths[0])
                if first_image is None:
                    raise RuntimeError(f"无法读取第一张图片: {self.image_paths[0]}")
                h, w = first_image.shape[:2]
                self.size = (w, h)

            # 创建视频写入器（尝试使用高质量编码器）
            # 尝试使用H.265/HEVC编码器（更高压缩率和质量）
            fourcc = cv2.VideoWriter_fourcc(*'hev1')
            writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, self.size)
            
            # 如果HEVC不可用，尝试H.264
            if not writer.isOpened():
                fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264编码
                writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, self.size)
                
                # 如果H.264不可用，回退到mp4v
                if not writer.isOpened():
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, self.size)
                    
                    if not writer.isOpened():
                        raise RuntimeError("无法创建视频文件，请检查参数和路径")

            # 处理每张图片
            total = len(self.image_paths)
            for i, img_path in enumerate(self.image_paths):
                if not self._is_running:
                    break

                frame = cv2.imread(img_path)
                if frame is None:
                    raise RuntimeError(f"无法读取图片: {img_path}")

                # 调整尺寸
                if frame.shape[1] != self.size[0] or frame.shape[0] != self.size[1]:
                    # 选择插值方法（基于质量设置）
                    if self.quality == 0:  # 高质量
                        interpolation = cv2.INTER_CUBIC  # 立方插值，质量更高
                    elif self.quality == 1:  # 标准
                        interpolation = cv2.INTER_LINEAR  # 线性插值，平衡速度和质量
                    else:  # 压缩
                        interpolation = cv2.INTER_AREA  # 区域插值，适合缩小图像
                    
                    if self.keep_aspect:
                        # 保持宽高比
                        scale = min(self.size[0] / frame.shape[1], self.size[1] / frame.shape[0])
                        new_w = int(frame.shape[1] * scale)
                        new_h = int(frame.shape[0] * scale)
                        frame = cv2.resize(frame, (new_w, new_h), interpolation=interpolation)
                        
                        # 填充黑边
                        canvas = np.zeros((self.size[1], self.size[0], 3), dtype=np.uint8)
                        x = (self.size[0] - new_w) // 2
                        y = (self.size[1] - new_h) // 2
                        canvas[y:y+new_h, x:x+new_w] = frame
                        frame = canvas
                    else:
                        # 直接拉伸
                        frame = cv2.resize(frame, self.size, interpolation=interpolation)

                writer.write(frame)
                self.progress_updated.emit(int((i + 1) * 100 / total))

            writer.release()
            if self._is_running:
                self.finished.emit(self.output_path)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._is_running = False


class ImageToVideoApp(QMainWindow):
    """主应用程序窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图像转视频工具")
        self.setGeometry(100, 100, 600, 500)  # 增加窗口高度
        self._init_ui()
        self.worker_thread = None
        self.image_paths = []  # 初始化图片路径列表

    def _init_ui(self):
        """初始化UI"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # 图片选择区域
        image_group = QWidget()
        image_layout = QVBoxLayout()
        image_group.setLayout(image_layout)

        self.image_list_label = QLabel("已选择 0 张图片")
        image_layout.addWidget(self.image_list_label)

        # 图片选择按钮组
        btn_layout = QHBoxLayout()
        
        btn_select_images = QPushButton("选择图片")
        btn_select_images.setToolTip("从单个文件夹选择多张图片")
        btn_select_images.clicked.connect(self._select_images)
        btn_layout.addWidget(btn_select_images)
        
        btn_add_folder = QPushButton("添加文件夹")
        btn_add_folder.setToolTip("添加整个文件夹中的图片")
        btn_add_folder.clicked.connect(self._add_folder_images)
        btn_layout.addWidget(btn_add_folder)
        
        btn_add_images = QPushButton("添加更多图片")
        btn_add_images.setToolTip("添加更多图片到当前选择")
        btn_add_images.clicked.connect(self._add_more_images)
        btn_layout.addWidget(btn_add_images)
        
        btn_clear_images = QPushButton("清除选择")
        btn_clear_images.setToolTip("清除所有已选图片")
        btn_clear_images.clicked.connect(self._clear_images)
        btn_layout.addWidget(btn_clear_images)
        
        image_layout.addLayout(btn_layout)
        
        # 排序按钮
        sort_layout = QHBoxLayout()
        btn_sort_name = QPushButton("按名称排序")
        btn_sort_name.clicked.connect(self._sort_by_name)
        sort_layout.addWidget(btn_sort_name)
        
        btn_sort_date = QPushButton("按日期排序")
        btn_sort_date.clicked.connect(self._sort_by_date)
        sort_layout.addWidget(btn_sort_date)
        
        image_layout.addLayout(sort_layout)

        # 添加富文本框显示图片路径
        self.image_paths_text = QTextEdit()
        self.image_paths_text.setReadOnly(True)
        self.image_paths_text.setPlaceholderText("选择的图片路径将显示在这里")
        image_layout.addWidget(self.image_paths_text)

        layout.addWidget(image_group)

        # 输出设置区域
        output_group = QWidget()
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)

        # 输出路径
        output_path_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("输出视频路径")
        output_path_layout.addWidget(self.output_path_edit)

        btn_select_output = QPushButton("选择")
        btn_select_output.clicked.connect(self._select_output_path)
        output_path_layout.addWidget(btn_select_output)
        output_layout.addLayout(output_path_layout)

        # 视频参数
        param_layout = QHBoxLayout()

        # 帧率
        fps_layout = QVBoxLayout()
        fps_layout.addWidget(QLabel("帧率 (FPS)"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 120)
        self.fps_spin.setValue(30)
        fps_layout.addWidget(self.fps_spin)
        param_layout.addLayout(fps_layout)

        # 尺寸
        size_layout = QVBoxLayout()
        size_layout.addWidget(QLabel("视频尺寸"))
        self.size_combo = QComboBox()
        self.size_combo.addItems([
            "自动 (使用第一张图片尺寸)", 
            "3840x2160 (4K UHD)",
            "2560x1440 (2K QHD)",
            "1920x1080 (Full HD)",
            "1280x720 (HD)",
            "640x480 (SD)",
            "自定义..."
        ])
        self.size_combo.currentIndexChanged.connect(self._on_size_changed)
        size_layout.addWidget(self.size_combo)
        
        # 自定义尺寸输入
        self.custom_size_widget = QWidget()
        self.custom_size_layout = QHBoxLayout(self.custom_size_widget)
        self.width_edit = QSpinBox()
        self.width_edit.setRange(32, 7680)  # 最大支持8K
        self.width_edit.setValue(1920)
        self.width_edit.setSuffix(" px")
        self.height_edit = QSpinBox()
        self.height_edit.setRange(32, 4320)
        self.height_edit.setValue(1080)
        self.height_edit.setSuffix(" px")
        self.custom_size_layout.addWidget(self.width_edit)
        self.custom_size_layout.addWidget(QLabel("x"))
        self.custom_size_layout.addWidget(self.height_edit)
        size_layout.addWidget(self.custom_size_widget)
        self.custom_size_widget.setVisible(False)  # 默认隐藏
        
        param_layout.addLayout(size_layout)

        # 宽高比
        aspect_layout = QVBoxLayout()
        aspect_layout.addWidget(QLabel("宽高比"))
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(["保持宽高比", "拉伸填充"])  # 0=保持, 1=拉伸
        aspect_layout.addWidget(self.aspect_combo)
        param_layout.addLayout(aspect_layout)
        
        # 视频质量
        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel("视频质量"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["高质量", "标准", "压缩"])
        self.quality_combo.setToolTip("高质量：更清晰但文件更大\n标准：平衡质量和文件大小\n压缩：文件小但质量较低")
        quality_layout.addWidget(self.quality_combo)
        param_layout.addLayout(quality_layout)

        output_layout.addLayout(param_layout)
        layout.addWidget(output_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # 生成按钮
        btn_generate = QPushButton("生成视频")
        btn_generate.clicked.connect(self._generate_video)
        layout.addWidget(btn_generate)

    def _select_images(self):
        """选择图片（替换当前选择）"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;所有文件 (*)")
        
        if files:
            self.image_paths = files
            self._update_image_list()
    
    def _add_more_images(self):
        """添加更多图片（保留当前选择）"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "添加更多图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;所有文件 (*)")
        
        if files:
            self.image_paths.extend(files)
            self._update_image_list()
    
    def _add_folder_images(self):
        """添加整个文件夹的图片"""
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder:
            # 支持的图片扩展名
            extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff']
            
            # 获取文件夹中所有图片
            new_images = []
            for ext in extensions:
                new_images.extend(list(Path(folder).glob(f"*{ext}")))
                new_images.extend(list(Path(folder).glob(f"*{ext.upper()}")))
            
            # 转换为字符串路径并添加到当前列表
            if new_images:
                new_image_paths = [str(img) for img in new_images]
                self.image_paths.extend(new_image_paths)
                self._update_image_list()
    
    def _clear_images(self):
        """清除所有已选图片"""
        self.image_paths = []
        self._update_image_list()
    
    def _sort_by_name(self):
        """按文件名排序图片"""
        if self.image_paths:
            self.image_paths.sort(key=lambda x: Path(x).name)
            self._update_image_list()
    
    def _sort_by_date(self):
        """按文件修改日期排序图片"""
        if self.image_paths:
            self.image_paths.sort(key=lambda x: os.path.getmtime(x))
            self._update_image_list()
    
    def _update_image_list(self):
        """更新图片列表显示"""
        count = len(self.image_paths)
        self.image_list_label.setText(f"已选择 {count} 张图片")
        self.image_paths_text.setPlainText('\n'.join(self.image_paths))

    def _select_output_path(self):
        """选择输出路径"""
        dialog = QFileDialog()
        options = dialog.options()
        file, _ = QFileDialog.getSaveFileName(
            self, "保存视频", "", 
            "MP4视频 (*.mp4);;AVI视频 (*.avi);;所有文件 (*)",
            options=options)
        
        if file:
            self.output_path_edit.setText(file)

    def _on_size_changed(self, index):
        """处理分辨率选择变化"""
        is_custom = self.size_combo.currentText() == "自定义..."
        self.custom_size_widget.setVisible(is_custom)
        
    def _get_video_size(self) -> Optional[Tuple[int, int]]:
        """获取视频尺寸"""
        text = self.size_combo.currentText()
        if text.startswith("自动"):
            return None
        
        try:
            if text == "自定义...":
                # 使用自定义尺寸
                w = self.width_edit.value()
                h = self.height_edit.value()
            else:
                # 从预设中提取尺寸
                size_part = text.split(" ")[0]  # 提取 "1920x1080" 部分
                w, h = map(int, size_part.split("x"))
            
            # 确保尺寸是偶数（某些编码器要求）
            w = w if w % 2 == 0 else w + 1
            h = h if h % 2 == 0 else h + 1
            
            return (w, h)
        except Exception:
            return None

    def _generate_video(self):
        """生成视频"""
        if not self.image_paths:
            QMessageBox.warning(self, "警告", "请先选择图片")
            return
        
        output_path = self.output_path_edit.text().strip()
        if not output_path:
            QMessageBox.warning(self, "警告", "请指定输出视频路径")
            return
            
        # 确认图片数量
        if len(self.image_paths) > 100:
            reply = QMessageBox.question(
                self, "确认", 
                f"您选择了 {len(self.image_paths)} 张图片，处理可能需要一些时间。是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        try:
            # 获取参数
            fps = self.fps_spin.value()
            size = self._get_video_size()
            keep_aspect = self.aspect_combo.currentIndex() == 0
            quality = self.quality_combo.currentIndex()  # 0=高质量, 1=标准, 2=压缩
            
            # 创建并启动工作线程
            self.worker_thread = VideoGeneratorThread(
                self.image_paths, output_path, fps, size, keep_aspect, quality)
            
            self.worker_thread.progress_updated.connect(self._update_progress)
            self.worker_thread.finished.connect(self._generation_finished)
            self.worker_thread.error_occurred.connect(self._generation_error)
            
            self.progress_bar.setValue(0)
            self.worker_thread.start()
            
            # 禁用UI控件
            self._set_ui_enabled(False)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化失败: {str(e)}")

    def _update_progress(self, value: int):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def _generation_finished(self, output_path: str):
        """视频生成完成"""
        self._set_ui_enabled(True)
        QMessageBox.information(self, "完成", f"视频已成功生成:\n{output_path}")

    def _generation_error(self, error_msg: str):
        """视频生成错误"""
        self._set_ui_enabled(True)
        QMessageBox.critical(self, "错误", f"生成视频失败:\n{error_msg}")

    def _set_ui_enabled(self, enabled: bool):
        """设置UI控件的启用状态"""
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QPushButton, QComboBox, QSpinBox, QLineEdit)):
                widget.setEnabled(enabled)

    def closeEvent(self, event):
        """关闭窗口事件"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = ImageToVideoApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()