import os
from PIL import Image, ImageDraw, ImageFont
import jieba

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
    # Parse JSON data
    paragraphs = json_data["paragraphs_result"]
    
    # Open the image and convert to RGB
    img = Image.open(image_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    
    for para in paragraphs:
        # Extract coordinates and dimensions
        top = para["top"]
        left = para["left"]
        width = para["width"]
        height = para["height"]
        
        # Ensure coordinates are within image boundaries
        left = max(0, left)
        top = max(0, top)
        width = min(img_width - left, width)
        height = min(img_height - top, height)
        
        # Draw white rectangle
        draw.rectangle([(left, top), (left + width, top + height)], fill="white")
        
        # Prepare text by joining words and segmenting with jieba
        words = para["words"]
        text = ''.join(words)
        segmented_text = ' '.join(jieba.lcut(text))
        
        # Define font properties
        max_font_size = 48
        min_font_size = 8
        font_name = "Arial Unicode MS.TTF"  
        
        # Function to wrap text
        def wrap_text(text, font, max_width, draw):
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                temp_line = current_line + word + " "
                if draw.textlength(temp_line, font=font) <= max_width:
                    current_line = temp_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)
            return lines
        
        # Find suitable font size
        font_size = max_font_size
        font = ImageFont.truetype(font_name, font_size)
        lines = wrap_text(segmented_text, font, width, draw)
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
        text_height = line_height * len(lines)
        
        while text_height > height and font_size > min_font_size:
            font_size -= 1
            font = ImageFont.truetype(font_name, font_size)
            lines = wrap_text(segmented_text, font, width, draw)
            ascent, descent = font.getmetrics()
            line_height = ascent + descent
            text_height = line_height * len(lines)
        
        # If even the smallest font doesn't fit, use the smallest possible
        if font_size < min_font_size:
            font_size = min_font_size
            font = ImageFont.truetype(font_name, font_size)
            lines = wrap_text(segmented_text, font, width, draw)
            ascent, descent = font.getmetrics()
            line_height = ascent + descent
            text_height = line_height * len(lines)
        
        # Calculate starting position to center the text
        max_text_width = max(draw.textlength(line, font=font) for line in lines)
        x = left + (width - max_text_width) / 2
        y = top + (height - text_height) / 2 + ascent  # Adjust y for ascent
        
        # Draw each line
        for line in lines:
            draw.text((x, y), line, font=font, fill="black")
            y += line_height
    
    # Save the image
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    file_name = os.path.basename(image_path)
    name, ext = os.path.splitext(file_name)
    output_path = os.path.join(output_folder, f"{name}_yutori{ext}")
    img.save(output_path)
    
    # 完成后打开文件夹
    if os.name == 'nt':  # Windows
        os.startfile(output_folder)
    elif os.name == 'posix':  # macOS/Linux
        subprocess.call(['open', output_folder])