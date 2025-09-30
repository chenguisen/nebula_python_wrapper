import numpy as np
from stl import mesh
import os
import sys
import argparse

# 常量定义
SCALE_FACTOR = 20  # 坐标缩放因子
POSITIVE_MARKER = "0 -123"  # 正向法向量标记
NEGATIVE_MARKER = "-123 0"  # 负向法向量标记
PROGRESS_INTERVAL = 10000  # 进度显示间隔

def process_stl_to_tri(input_path, output_path=None, scale_factor=SCALE_FACTOR):
    """
    将STL文件转换为指定格式的TRI文件
    
    参数:
        input_path: 输入STL文件路径
        output_path: 输出TRI文件路径(可选)
        scale_factor: 坐标缩放因子(默认为20)
    
    返回:
        写入的三角形数量和输出文件路径
    """
    # 设置默认输出路径
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.tri"
    
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
            
        # 加载STL模型
        stl_mesh = mesh.Mesh.from_file(input_path)
        
        # 获取三角形数量
        num_triangles = len(stl_mesh.vectors)
        print(f"发现 {num_triangles} 个三角形")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 打开输出文件
        with open(output_path, 'w') as f:
            # 处理每个三角形
            for i, triangle in enumerate(stl_mesh.vectors):
                # 获取法向量
                normal = stl_mesh.normals[i] if i < len(stl_mesh.normals) else None
                
                # 确定法向量方向标记
                marker = POSITIVE_MARKER if (normal is None or np.sum(normal) >= 0) else NEGATIVE_MARKER
                
                # 获取三角形的三个顶点坐标
                v1, v2, v3 = triangle
                
                # 创建格式化的顶点字符串（应用缩放因子）
                vertices_str = " ".join(f"{(coord * scale_factor):.6f}" for vertex in [v1, v2, v3] for coord in vertex)
                
                # 写入一行
                line = f"{marker} {vertices_str}\n"
                f.write(line)
                
                # 显示进度
                if (i + 1) % PROGRESS_INTERVAL == 0:
                    print(f"已处理 {i+1} 个三角形...")
        
        print(f"转换完成! 输出文件: {output_path}")
        return num_triangles, output_path
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 0, None

def _build_cli():
    parser = argparse.ArgumentParser(description='Convert STL to TRI format')
    parser.add_argument('input_stl', help='Path to input .stl file')
    parser.add_argument('output_tri', nargs='?', help='Path to output .tri file; default: <input>.tri')
    parser.add_argument('--scale', type=float, default=SCALE_FACTOR, help='Scale factor for coordinates (default: %(default)s)')
    return parser

def main():
    parser = _build_cli()
    args = parser.parse_args()
    process_stl_to_tri(args.input_stl, args.output_tri, scale_factor=args.scale)

if __name__ == '__main__':
    main()

