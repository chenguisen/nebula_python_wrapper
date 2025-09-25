import json
def add_frame_to_parameters(parameters, file_path, rotation, translation):
    """
    向 parameters 字典中的 frames 列表添加新的帧数据。
    
    参数:
        parameters (dict): 包含相机参数和帧数据的字典。
        file_path (str): 新帧的图片路径。
        rotation (list): 新帧的旋转参数 [rx, ry, rz]。
        translation (list): 新帧的平移参数 [tx, ty, tz]。
    
    返回:
        dict: 更新后的 parameters 字典。
    """
    # 确保 frames 键存在
    if "frames" not in parameters:
        parameters["frames"] = []
    
    # 添加新帧数据
    new_frame = {
        "file_path": file_path,
        "rotation": rotation,
        "translation": translation
    }
    parameters["frames"].append(new_frame)
    
    return parameters
def save_parameters(parameters, file_path):
    """
    保存相机参数和帧数据到 JSON 文件。
    
    参数:
        parameters (dict): 包含相机参数和帧数据的字典，格式如下：
            {
                "camera": {
                    "width": int,
                    "height": int,
                    "cx": float,
                    "cy": float
                },
                "frames": [
                    {
                        "file_path": str,
                        "rotation": [float, float, float],
                        "translation": [float, float, float]
                    },
                    ...
                ]
            }
        file_path (str): 保存 JSON 文件的路径。
    """
    with open(file_path, 'w') as f:
        json.dump(parameters, f, indent=4)

# 示例用法
if __name__ == "__main__":
    example_parameters = {
        "camera": {
            "width": 1024,
            "height": 1024,
            "cx": 512.0,
            "cy": 512.0
        },
        "frames": [
            {
                "file_path": "images/view_000.png",
                "rotation": [0.0, 0.0, 0.0],
                "translation": [0.0, 0.0, 0.0]
            },
            {
                "file_path": "images/view_001.png",
                "rotation": [0.0, 55.0, 0.0],
                "translation": [0.0, 0.0, 0.0]
            }
        ]
    }
    save_parameters(example_parameters, "example_parameters.json")