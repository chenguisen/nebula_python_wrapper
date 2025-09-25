import sys
import pathlib
import torch
import numpy as np
from sem_pri import generate_sem_pri_data
from voxel_to_mesh import run_interface
# 示例用法
# 可以使用任意文件名作为输入，包括包含空格和特殊字符的文件名，程序会保留原始文件名
# 例如：
# voxel_path = '/path/to/your/input/file with spaces.stl'  # 包含空格的文件名
# mesh_path = '/path/to/output directory/'  # 包含空格的目录
# run_interface(voxel_path, mesh_path, final_side=1000)
#
# 或者从命令行运行时：
# python voxel_to_mesh.py "/path/to/file with spaces.stl" "/output directory/"

# 如果需要从命令行运行，可以使用以下代码：
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从命令行获取输入文件路径，确保正确处理包含空格的文件名
        input_file = sys.argv[1]
        
        # 处理引号包裹的文件名（可能包含空格）
        if (input_file.startswith('"') and input_file.endswith('"')) or \
           (input_file.startswith("'") and input_file.endswith("'")):
            input_file = input_file[1:-1]
        
        # 默认输出目录为输入文件所在目录
        output_dir = pathlib.Path(input_file).parent
        
        if len(sys.argv) > 2:
            # 如果提供了输出目录，则使用提供的输出目录
            output_dir = sys.argv[2]
            # 处理引号包裹的目录名（可能包含空格）
            if (output_dir.startswith('"') and output_dir.endswith('"')) or \
               (output_dir.startswith("'") and output_dir.endswith("'")):
                output_dir = output_dir[1:-1]
        
        print(f"处理文件: {input_file}")
        print(f"输出目录: {output_dir}")
        
        # 确保路径正确处理，特别是包含空格的路径
        run_interface(input_file, output_dir, final_side=512)
    else:
        # 默认示例


        # 离子束成像
        # 探测器的倾转角常见的有55度、52度。
        # 此时离子束发射方向相对探测器平面是垂直的。
        # 此时，离子束成像就转换为探测器的倾转角为0度的成像情况，离子束反射方向也变为沿z轴。
        # 一般情况下，用离子束成像时，样品倾转角和探测器倾转角是相同的，也即样品不用倾转；当然，样品也可以随意倾转。
    


        # 电子束成像
        # 探测器的倾转角为76.8度
        # 电子束的入射方向是固定的，沿z轴方向，即电子束的倾转角为0度。
        # 样品则可以随意倾转。


        # 总之，电子束和离子束都不用倾转。


        # 应当有必要，为了更快的模拟速度，应该进行一个scale，即应当使用final_side进行缩放  
        voxel_path = pathlib.Path('/home/chenguisen/AISI/nebula/nebula_python_wrapper/data/4_Trench Milling.stl')
        mesh_path = pathlib.Path('/home/chenguisen/AISI/nebula/nebula_python_wrapper/data')
        electron_ion_um = {"ion_beam": "ion_beam", "electron_beam": "electron_beam"}

        sample_tilt_x = 0
        det_tilt_x = 0
        beam_type = "ion_beam"
        if electron_ion_um["ion_beam"] == beam_type:
            # 1. 生成SEM PRI文件
            sample_tilt_x = 55    # 样品倾转角
        elif electron_ion_um["electron_beam"] == beam_type:
            # 2. 生成SEM PRI文件
            sample_tilt_x = 0   # 样品倾转角,可选择任意角度
            det_tilt_x = 76.8  # 探测器倾转角  
        else:
            raise ValueError("electron_ion_um must be 'ion_beam' or 'electron_beam'")
        
        v, faces, d_zmin, d_zmax = run_interface(voxel_path, mesh_path, final_side=1000,sample_tilt_x=sample_tilt_x,sample_tilt_new_z=0, det_tilt_x=det_tilt_x)

        x_min = int(np.floor(torch.min(v[:, 0]).cpu()))
        x_max = int(np.ceil(torch.max(v[:, 0]).cpu()))   
        y_min = int(np.floor(torch.min(v[:, 1]).cpu()))
        y_max = int(np.ceil(torch.max(v[:, 1]).cpu()))   
        
        print("x_min, x_max, y_min, y_max = ", x_min, x_max, y_min, y_max)


        pixel_size =2     # in nanometer
        x_pixel_num = int((np.abs(x_max)+np.abs(x_min))/pixel_size+1)
        y_pixel_num = int((np.abs(y_max)+np.abs(y_min))/pixel_size+1)


        xpx = np.linspace(x_min, x_max, x_pixel_num)
        ypx = np.linspace(y_min, y_max, y_pixel_num)
        print(x_pixel_num, y_pixel_num)
        


        beam_incident_dir = np.array([0, 0, -1])  # 束入射方向
        print("beam_incident_dir = ",beam_incident_dir)
        beam_zmax = (d_zmax+d_zmin)/2
        print("beam_zmax = ",beam_zmax)

        

        generate_sem_pri_data(
            z=beam_zmax,
            xpx=xpx,
            ypx=ypx,
            energy=500,
            epx=500,
            sigma=1,
            poisson=True,
            dx=beam_incident_dir[0],
            dy=beam_incident_dir[1],
            dz=beam_incident_dir[2],
            file_path=mesh_path/'sem.pri'
        )
       
        
