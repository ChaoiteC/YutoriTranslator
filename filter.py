import os

from PIL import Image

def get_all_image_paths(paths):
    image_paths = []
    for path in paths:
        if os.path.isfile(path) and path.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_paths.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                        image_paths.append(file_path)
    return image_paths

def is_valid_image(file_path):
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            if not (30 <= min(width, height) and max(width, height) <= 4096):
                return False, "图片尺寸超出范围（30px 到 4096px）。"
            if not (1 / 3 <= width / height <= 3):
                return False, "图片长宽比不在 3:1 以内。"
            if os.path.getsize(file_path) > 4 * 1024 * 1024:
                return False, "图片大小超过 4MB。"
            return True, None
    except (IOError, SyntaxError):
        return False, "文件不是有效的图片。"

def filter_images(paths, main_window):
    image_paths = get_all_image_paths(paths)
    valid_paths = []

    total_images = len(image_paths)
    for i, image_path in enumerate(image_paths):
        main_window.output_text_ctrl.AppendText(f"[{i+1}/{total_images}]\n")
        is_valid, error_msg = is_valid_image(image_path)
        if is_valid:
            valid_paths.append(image_path)
        else:
            main_window.output_text_ctrl.AppendText(f"无效图片: {image_path}\n- {error_msg}\n")

    return valid_paths
