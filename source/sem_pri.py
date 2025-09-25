import numpy as np
import os
import sys
import time

"""
SEM Image Simulation Generator

此脚本生成扫描电子显微镜(SEM)图像模拟数据，创建包含电子束数据的.pri文件。
.pri文件格式存储每个模拟电子的位置、方向、能量和像素信息。

输出:
- sem.pri: 包含电子数据的二进制文件
"""
def generate_sem_pri_data(
        z: float, 
        xpx: np.ndarray, 
        ypx: np.ndarray, 
        energy:float = 500, 
        epx: int=1000, 
        sigma:float = 1,
        poisson: bool = True, 
        dx: float = 0, 
        dy: float = 0, 
        dz: float = -1, 
        file_path: str = 'sem.pri'
        ):
    """
    # 参数设置:
    z = 150                            # 起始z位置 (nm)
    xpx = np.linspace(-128, 128, 512)  # x像素: 范围从-200nm到+200nm, 步长为2nm
    ypx = np.linspace(-128, 128, 512)  # y像素: 范围从-200nm到+200nm, 步长为2nm
    energy = 500                      # 电子束能量, 单位eV
    epx = 1000                        # 每个像素的电子数量(使用泊松分布时为平均值)
    sigma = 1                         # 高斯光束斑点大小的标准差 (nm)
    poisson = True                    # 是否使用泊松散粒噪声
    dx = 0                           # x方向的方向向量
    dy = 0                           # y方向的方向向量
    dz = -1                          # z方向的方向向量
    """
   
    # 计算实际步长
    x_range = xpx[-1] - xpx[0]  # 动态计算x方向的范围
    y_range = ypx[-1] - ypx[0]  # 动态计算y方向的范围
    x_step = x_range / (len(xpx) - 1)
    y_step = y_range / (len(ypx) - 1)
    print(f"x方向的步长: {x_step:.4f} nm")
    print(f"y方向的步长: {y_step:.4f} nm")

    # 这是一个对应pri文件格式的numpy数据类型
    electron_dtype = np.dtype([
        ('x',  '=f'), ('y',  '=f'), ('z',  '=f'), # 位置
        ('dx', '=f'), ('dy', '=f'), ('dz', '=f'), # 方向
        ('E',  '=f'),                             # 能量
        ('px', '=i'), ('py', '=i')])              # 像素索引

    #print(f"输出文件: {file_path}")

    try:
       
        # 估算内存使用和文件大小
        pixel_count = len(xpx) * len(ypx)
        avg_electrons = epx * pixel_count
        memory_estimate = avg_electrons * electron_dtype.itemsize / (1024*1024)  # MB
        print(f"像素总数: {pixel_count}")
        print(f"预计电子总数: {avg_electrons:,}")
        print(f"预计内存使用: {memory_estimate:.2f} MB")
        print(f"预计文件大小: {memory_estimate:.2f} MB")
        
        # 方向向量归一化因子 (对于(0,0,-1)向量，归一化因子为1)
        norm_factor = 1.0
        
        total_electrons = 0
        start_time = time.time()
        
        print("开始生成SEM数据...")
        with open(file_path, 'wb') as file:
            # 遍历像素
            for i, xmid in enumerate(xpx):
                # 每处理10%的像素显示一次进度
                if i % (len(xpx) // 10) == 0 and i > 0:
                    percent = i * 100 // len(xpx)
                    elapsed = time.time() - start_time
                    remaining = elapsed * (len(xpx) - i) / i
                    print(f"进度: {percent}%, 已处理电子数: {total_electrons}, "
                        f"已用时间: {elapsed:.1f}秒, 预计剩余: {remaining:.1f}秒")
                    
                for j, ymid in enumerate(ypx):
                    try:
                        # 计算此像素的电子数量
                        N_elec = np.random.poisson(epx) if poisson else epx
                        total_electrons += N_elec
                        
                        # 分批处理大量电子以节省内存
                        batch_size = min(N_elec, 10000)  # 每批最多处理10000个电子
                        
                        for batch_start in range(0, N_elec, batch_size):
                            batch_end = min(batch_start + batch_size, N_elec)
                            batch_count = batch_end - batch_start
                            
                            # 分配numpy缓冲区
                            buffer = np.empty(batch_count, dtype=electron_dtype)
                            
                            # 填充数据
                            buffer['x'] = np.random.normal(xmid, sigma, batch_count)
                            buffer['y'] = np.random.normal(ymid, sigma, batch_count)
                            buffer['z'] = z
                            buffer['dx'] = dx
                            buffer['dy'] = dy
                            buffer['dz'] = dz * norm_factor  # 使用归一化的方向向量
                            buffer['E'] = energy
                            buffer['px'] = i
                            buffer['py'] = j
                            
                            # 写入文件
                            buffer.tofile(file)
                    except Exception as e:
                            # 如果发生错误，打印错误信息并继续处理下一个像素
                            raise RuntimeError(f"处理像素({i},{j})时出错: {str(e)}")        
        total_time = time.time() - start_time
        print(f"完成! 总共处理了 {total_electrons:,} 个电子")
        print(f"总用时: {total_time:.2f} 秒")
        print(f"处理速度: {total_electrons/total_time:.2f} 电子/秒")
        print(f"文件已保存到: {file_path}")
        
    except Exception as e:
        #print(f"错误: {str(e)}")
        sys.exit(1)