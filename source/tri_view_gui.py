from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLineEdit, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
import os
import subprocess
import time
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

class TriVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        # 设置日志记录器
        self.logger = logging.getLogger('nebula_viewer.TriVisualizer')
        self.logger.info("Initializing TriVisualizer")
        
        self.setWindowTitle("Tri 文件可视化工具")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
                
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        self.file_path_display.setPlaceholderText("文件路径将显示在这里")
        self.layout.addWidget(self.file_path_display)
        
        self.button = QPushButton("选择文件")
        self.button.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.button)
        
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 启用 JavaScript 和插件
        settings = self.web_view.settings()
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(settings.WebAttribute.PluginsEnabled, True)
        
        # 设置用户代理，模拟 Chrome 浏览器
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setDefaultTextEncoding("utf-8")
        
        # 启用开发者工具
        
        
        # 设置自定义 WebEnginePage 以拦截链接点击和处理控制台消息
        custom_page = WebEnginePage(self.web_view)
        self.web_view.setPage(custom_page)
        
        # 无需手动连接信号，WebEnginePage 类已处理 JavaScript 控制台消息
        
        self.layout.addWidget(self.web_view)
        
        # 保存开发服务器进程对象
        self.dev_server_process = None
        
        # 启动时直接加载本地开发服务器页面
        from PyQt6.QtCore import QUrl
        self.web_view.load(QUrl("http://localhost:5173/"))
        self.label.setText("正在加载可视化页面...")
        self.logger.info("Loading visualization page")
        
    # 定义 JavaScript 控制台消息信号
    javaScriptConsoleMessage = pyqtSignal(int, str, int, str)

    def handle_console_message(self, level, message, line, source_id):
        """处理 JavaScript 控制台消息"""
        try:
            level_str = ["Info", "Warning", "Error"][level] if isinstance(level, int) and 0 <= level < 3 else "Unknown"
            log_msg = f"JS Console ({level_str}): {message} [line: {line}, source: {source_id}]"
            
            # 根据日志级别选择不同的日志方法
            if level_str == "Error":
                self.logger.error(log_msg)
            elif level_str == "Warning":
                self.logger.warning(log_msg)
            else:
                self.logger.debug(log_msg)
                
            self.javaScriptConsoleMessage.emit(level, message, line, source_id)
        except Exception as e:
            self.logger.error(f"Error handling console message: {str(e)}")

    def open_file_dialog(self):
        """
        打开文件选择对话框并加载可视化页面
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 .tri 文件", "", "Tri 文件 (*.tri);;所有文件 (*)")
        if file_path:
            self.file_path_display.setText(file_path)
            self.load_visualization(file_path)
    
    def load_visualization(self, file_path):
        """
        加载 .tri 文件内容并可视化
        """
        if not os.path.exists(file_path):
            self.label.setText(f"错误: 文件 {file_path} 不存在")
            return
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            
            # 直接加载文件内容并设置 MIME 类型
            # 完整的MIME类型映射
            mime_map = {
                '.json': 'application/json',
                '.tri': 'text/plain',
                '.txt': 'text/plain',
                '.csv': 'text/csv',
                '.hdr': 'text/plain',
                '.dat': 'application/octet-stream'
            }
            mime_type = 'application/octet-stream'  # 默认类型
            for ext in mime_map:
                if file_path.lower().endswith(ext):
                    mime_type = mime_map[ext]
                    break
            
            self.web_view.setContent(file_content.encode('utf-8'), mime_type)
            self.label.setText(f"已加载文件: {os.path.basename(file_path)}")
            
            # 优化的服务器检查(带重试)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with urlopen("http://localhost:5173", timeout=5) as response:
                        if response.status == 200:
                            break
                        elif attempt == max_retries - 1:
                            self.label.setText("错误: 开发服务器异常")
                            return
                except Exception as e:
                    if attempt == max_retries - 1:
                        self.label.setText(f"错误: 无法连接开发服务器 ({str(e)})")
                        return
                    time.sleep(1)
            
            try:
                self.label.setText("开发服务器已启动")
            except Exception as e:
                self.label.setText(f"错误: 无法启动开发服务器。请确保已安装 Node.js 并运行 `npm install`。详细信息: {str(e)}")
                print(f"DEBUG - 开发服务器启动失败: {str(e)}")
                return
            
            # 加载本地开发服务器页面
            from PyQt6.QtCore import QUrl
            from urllib.parse import quote
            import mimetypes
            
            # 确保 MIME 类型已正确初始化
            mimetypes.init()
            
            # 正确编码文件路径，确保特殊字符被正确处理
            encoded_path = quote(file_path)
            
            # 安全的文件内容读取(限制大小和验证内容)
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            try:
                file_size = os.path.getsize(file_path)
                if file_size > MAX_FILE_SIZE:
                    self.label.setText(f"错误: 文件过大 ({file_size} > {MAX_FILE_SIZE} bytes)")
                    return
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    
                # 基本内容验证
                if not file_content.strip():
                    self.label.setText("错误: 文件内容为空")
                    return
                
                # 构建 URL，包含文件名
                file_name = os.path.basename(file_path)
                url = f"http://localhost:5173/?fileName={quote(file_name)}"
                
                # 加载 URL
                self.web_view.load(QUrl(url))
                
                # 设置自定义 HTTP 头，传递文件内容
                self.web_view.page().profile().setHttpAcceptLanguage("en-US,en;q=0.9")
                self.web_view.page().profile().setHttpUserAgent("Mozilla/5.0 NebulaViewer/1.0")
                
                # 将文件内容存储在本地存储中，以便前端访问
                # 使用分块存储方式处理大文件
                self.logger.debug(f"Storing file content in localStorage, size: {len(file_content)} bytes")
                script = f"""
                try {{
                    // 清除之前的内容
                    localStorage.removeItem('triFileContent');
                    localStorage.removeItem('triFileChunks');
                    
                    // 分块存储大文件内容，避免超出 localStorage 限制
                    const content = `{file_content}`;
                    const maxChunkSize = 512 * 1024; // 512KB chunks
                    
                    if (content.length <= maxChunkSize) {{
                        // 小文件直接存储
                        localStorage.setItem('triFileContent', JSON.stringify(content));
                        console.log('File content stored in localStorage, size: ' + content.length + ' bytes');
                    }} else {{
                        // 大文件分块存储
                        const chunks = Math.ceil(content.length / maxChunkSize);
                        console.log(`File too large (${content.length} bytes), splitting into ${chunks} chunks`);
                        
                        // 存储块数量
                        localStorage.setItem('triFileChunks', chunks.toString());
                        
                        // 存储每个块
                        for (let i = 0; i < chunks; i++) {{
                            const start = i * maxChunkSize;
                            const end = Math.min(start + maxChunkSize, content.length);
                            const chunk = content.substring(start, end);
                            localStorage.setItem(`triFileContent_${i}`, JSON.stringify(chunk));
                            console.log(`Chunk ${i} stored, size: ${chunk.length} bytes`);
                        }}
                        
                        console.log('All chunks stored in localStorage');
                    }}
                }} catch (error) {{
                    console.error('Error storing file content in localStorage:', error);
                }}
                """
                self.web_view.page().runJavaScript(script)
                
                self.label.setText(f"正在加载文件: {file_path}...")
            except Exception as e:
                self.label.setText(f"错误: 无法读取文件内容: {str(e)}")
                print(f"DEBUG - 文件读取错误: {str(e)}")
            
            # 在页面加载完成后更新状态
            def on_load_finished(ok):
                if ok:
                    self.label.setText("页面加载完成")
                    self.logger.info("Page loaded successfully")
                    
                    # 执行额外的 JavaScript 来验证文件内容是否正确加载
                    verify_script = """
                    (function() {
                        try {
                            const chunks = localStorage.getItem('triFileChunks');
                            if (chunks) {
                                return `File content loaded in ${chunks} chunks`;
                            } else {
                                const content = localStorage.getItem('triFileContent');
                                if (content) {
                                    return `File content loaded, size: ${content.length} bytes`;
                                } else {
                                    return 'No file content found in localStorage';
                                }
                            }
                        } catch (error) {
                            return `Error verifying file content: ${error.message}`;
                        }
                    })();
                    """
                    
                    def handle_verification(result):
                        self.logger.debug(f"File content verification: {result}")
                    
                    self.web_view.page().runJavaScript(verify_script, 0, handle_verification)
                else:
                    self.label.setText("错误: 页面加载失败")
                    self.logger.error("Page failed to load")
            
            self.web_view.loadFinished.connect(on_load_finished)
        except Exception as e:
            self.label.setText(f"错误: {str(e)}")
            print(f"DEBUG - Exception: {str(e)}")


class WebEnginePage(QWebEnginePage):
    """
    自定义 WebEnginePage 以拦截链接点击、导航请求和 JavaScript 错误
    """
    javaScriptConsoleMessage = pyqtSignal(int, str, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('nebula_viewer.WebEnginePage')
        self.logger.info("Initializing custom WebEnginePage")
    
    def acceptNavigationRequest(self, url, type_, isMainFrame):
        """
        拦截所有导航请求
        """
        self.logger.debug(f"Navigation request: {url.toString()}, type: {type_}, isMainFrame: {isMainFrame}")
        
        if type_ == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            self.logger.info(f"Link clicked: {url.toString()}")
            self.parent().load(url)
            return False
        return super().acceptNavigationRequest(url, type_, isMainFrame)
    
    def createWindow(self, type_):
        """
        拦截新窗口或标签页的打开请求
        """
        self.logger.debug(f"Create window request, type: {type_}")
        return WebEnginePage(self.parent())
    
    def javaScriptAlert(self, securityOrigin, msg):
        """
        拦截 JavaScript alert 对话框
        """
        self.logger.info(f"JavaScript alert: {msg}")
        return super().javaScriptAlert(securityOrigin, msg)
    
    def javaScriptConsoleMessage(self, level, message, line, sourceID):
        """
        拦截 JavaScript 控制台消息并发射信号
        """
        level_str = ["Info", "Warning", "Error"][level.value] if level.value >= 0 and level.value < 3 else "Unknown"
        self.logger.debug(f"JS Console ({level_str}): {message} [line: {line}, source: {sourceID}]")
        # 传递给父类处理
        super().javaScriptConsoleMessage(level, message, line, sourceID)

if __name__ == "__main__":
    import sys
    import os
    import logging
    
    # 配置日志记录
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('nebula_viewer.log')
        ]
    )
    logger = logging.getLogger('nebula_viewer')
    logger.info("Starting Nebula Viewer application")
    
    # 设置字体环境变量
    os.environ["FONTCONFIG_PATH"] = "/etc/fonts"
    os.environ["FONTCONFIG_FILE"] = "/etc/fonts/fonts.conf"
    logger.debug("Font environment variables set")
    
    # 忽略 MIME 缓存文件错误
    os.environ["QT_LOGGING_RULES"] = "xdg.mime=false;qt.webenginecontext.warning=false"
    logger.debug("QT logging rules set")
    
    try:
        app = QApplication(sys.argv)
        window = TriVisualizer()
        window.show()
        logger.info("Main window displayed")
        
        # 确保程序退出时终止开发服务器进程
        def on_about_to_quit():
            if window.dev_server_process:
                logger.info("Terminating dev server process")
                window.dev_server_process.terminate()
        
        app.aboutToQuit.connect(on_about_to_quit)
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)