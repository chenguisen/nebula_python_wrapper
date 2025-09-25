import subprocess
from analysis import sem_analysis
class nebula_gpu:
    def __init__(self, command, sem_simu_result:str, image_path:str):
        super().__init__()
        self.command = command
        self.sem_simu_result = sem_simu_result
        self.image_path = image_path
    def run(self):
        try:
            import select
            import time
            import re
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=0  # 无缓冲模式
            )

            progress_completed = False
            progress_100_time = None
            # 使用 select 监听标准输出和错误
            while True:
                reads = [process.stdout.fileno(), process.stderr.fileno()]
                ret = select.select(reads, [], [])
                for fd in ret[0]:                                           
                    if fd == process.stderr.fileno():
                        error = process.stderr.readline()
                        if error:
                            error_stripped = error.strip()
                            print(error_stripped)
                            # 检测是否为detected: 0
                            if "running: 0 | detected: 0" in error_stripped:
                                message = "检测到detected: 0，需要对输入进行优化"
                                print(message)
                                process.terminate()
                                return_code = 1
                                message2 = "nebula_gpu 运行结束，未检测到有效数据，请优化输入"
                                print(message2)
                                return
                            
                            # 检测进度是否为100.00%
                            if "Progress 100.00%" in error_stripped and not progress_completed:                       
                                message = "检测到进度100.00%，将在20秒后终止进程并展示结果"
                                print(message)
                                progress_completed = True
                                progress_100_time = time.time()
                                
                            # 如果已经检测到100%进度且已经过了5秒，则终止进程
                            if progress_completed and progress_100_time is not None and time.time() - progress_100_time >= 20:
                                message1 = "如果等待20秒完成，进程未自然结束，则终止进程并展示结果"
                                print(message1)
                                process.terminate()
                                message2 = "nebula_gpu 运行成功！"
                                print(message2)
                                self.show_image(plot=False, save=True)
                                return

                # 检查进程是否自然结束
                if process.poll() is not None:
                    message2 = "nebula_gpu 运行成功！"
                    print(message2)
                    self.show_image(plot=False, save=True)
                    break

        except Exception as e:
            error_msg = f"调用 nebula_gpu 时发生异常: {str(e)}"
            print(f"[ERROR] {error_msg}")  # 在终端打印异常信息
            print(error_msg)
    def show_image(self, plot = True, save = False):
            # 自动调用 sem-analysis.py
            try:
                print(f"开始调用 sem-analysis.py 展示图像，输出文件: {self.sem_simu_result}")
                sem_analysis(self.sem_simu_result, self.image_path, plot=plot, save=save)    
                print(f"sem-analysis.py 执行完成，展示图像完成")
            except Exception as e:
                error_msg = f"调用 sem-analysis.py 时发生异常: {str(e)}"
                print(error_msg)