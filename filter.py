import os
from PIL import Image, ImageDraw, ImageFont

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
        main_window.output_text_ctrl.AppendText(f"处理文件路径：[{i+1}/{total_images}]\n")
        is_valid, error_msg = is_valid_image(image_path)
        if is_valid:
            valid_paths.append(image_path)
        else:
            main_window.output_text_ctrl.AppendText(f"无效图片: {image_path}\n- {error_msg}\n")

    return valid_paths

def annotate_image(json_data, image_path):
    # 打开图像
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # 获取图像的宽度和高度
    img_width, img_height = image.size
    
    # 加载字体
    font_size = 20  # 字体大小
    font = ImageFont.truetype("Arial Unicode MS.TTF", font_size)
    
    # 解析JSON数据
    try:
        paragraphs = json_data["paragraphs_result"]
    except KeyError:
        raise ValueError("Invalid JSON format: 'paragraphs_result' key not found")
    
    # 用于存储所有words的列表
    words_list = []
    
    # 在图像上绘制红色数字序号
    for i, paragraph in enumerate(paragraphs):
        try:
            words = paragraph["words"]
            top = paragraph["top"]
            left = paragraph["left"]
        except KeyError:
            raise ValueError("Invalid JSON format: 'words', 'top', or 'left' key not found in paragraph")
        
        # 绘制红色数字序号
        draw.text((left, top), f"{i+1}", fill="red", font=font)
        
        # 将words添加到列表中
        words_list.append(words)
    
    # 计算新的图像高度
    padding = 20  # 空白区域的高度
    # Calculate max text width using getbbox
    max_text_width = max(font.getbbox(f"{i+1}. {words}")[2] - font.getbbox(f"{i+1}. {words}")[0] for i, words in enumerate(words_list))
    new_height = img_height + padding + len(words_list) * font_size
    
    # 创建新的图像
    new_image_width = max(img_width, max_text_width + 20)
    new_image = Image.new("RGB", (int(new_image_width), int(new_height)), color="white")
    new_image.paste(image, (0, 0))
    
    new_draw = ImageDraw.Draw(new_image)
    
    # 在空白区域输出words
    for i, words in enumerate(words_list):
        new_draw.text((10, img_height + padding + i * font_size), f"{i+1}. {words}", fill="black", font=font)
    
    # 创建输出文件夹
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 生成新的文件名
    base_name, ext = os.path.splitext(os.path.basename(image_path))
    new_file_name = f"{base_name}_YutoriTrans{ext}"
    output_path = os.path.join(output_folder, new_file_name)
    
    # 保存图像到输出文件夹
    new_image.save(output_path)
    print(f"Annotated image saved to {output_path}")
    
    # 完成后打开文件夹
    if os.name == 'nt':  # Windows
        os.startfile(output_folder)
    elif os.name == 'posix':  # macOS/Linux
        subprocess.call(['open', output_folder])