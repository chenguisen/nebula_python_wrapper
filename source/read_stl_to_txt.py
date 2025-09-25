import numpy as np
import struct

def parse_stl_binary(data):
    """
    解析二进制STL文件数据
    :param data: 二进制数据
    :return: 顶点列表
    """
    vertices = []
    header = data[0:80]
    num_triangles = struct.unpack('<I', data[80:84])[0]
    offset = 84
    for _ in range(num_triangles):
        normal = struct.unpack('<3f', data[offset:offset+12])
        v1 = struct.unpack('<3f', data[offset+12:offset+24])
        v2 = struct.unpack('<3f', data[offset+24:offset+36])
        v3 = struct.unpack('<3f', data[offset+36:offset+48])
        vertices.extend([v1, v2, v3])
        offset += 50
    return vertices

def read_stl_to_txt(stl_file_path, txt_file_path):
    """
    读取STL文件并写入TXT文件
    :param stl_file_path: STL文件路径
    :param txt_file_path: 输出的TXT文件路径
    """
    with open(stl_file_path, 'rb') as stl_file:
        data = stl_file.read()
    
    with open(txt_file_path, 'w') as txt_file:
            vertices = parse_stl_binary(data)
            for v in vertices:
                txt_file.write(f"{v[0]} {v[1]} {v[2]}\n")

if __name__ == "__main__":
    stl_file_path = "/home/chenguisen/AISI/nebula/nebula_python_wrapper/data/4_Trench Milling.stl"
    txt_file_path = "/home/chenguisen/AISI/nebula/nebula_python_wrapper/data/4_Trench Milling.txt"
    read_stl_to_txt(stl_file_path, txt_file_path)
