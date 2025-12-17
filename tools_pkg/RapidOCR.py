import os
import mss
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
from rich.console import Console

console = Console()

class TextRecognizer:
    def __init__(self):
        self._ocr_engine = None
    
    # 延迟初始化，避免启动时耗时
    @property
    def engine(self):
        if self._ocr_engine is None:
            console.print("[dim]正在初始化 RapidOCR...[/dim]")
            self._ocr_engine = RapidOCR()
        return self._ocr_engine

    def capture_region(self, region):
        """
        截取指定区域
        region: [x, y, w, h]
        """
        with mss.mss() as sct:
            monitor = {"left": region[0], "top": region[1], "width": region[2], "height": region[3]}
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img

    def _filter_right_side(self, result, img_width):
        """
        过滤掉右侧文本（通常是自己发送的消息）
        """
        filtered_lines = []
        for line in result:
            if line and len(line) >= 2:
                box = line[0] # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                # 计算中心点 X 坐标
                center_x = sum([p[0] for p in box]) / 4
                # 如果中心点在右侧 (大于宽度的 1/2)，则跳过
                if center_x > img_width / 2:
                    continue
                filtered_lines.append(line[1])
        return filtered_lines

    def extract_text(self, img, filter_right=False):
        """
        使用 RapidOCR 提取图像中的文本
        img: PIL Image 对象
        filter_right: 是否过滤掉右侧文本（通常是自己发送的消息）
        """
        try:
            # 1.pil image to numpy array
            img_np = np.array(img)
        
            # 2.rapidocr inference
            result, elapse = self.engine(img_np)
            
            if not result:
                return ""
            
            # 3.filter right side text
            if filter_right:
                img_width = img_np.shape[1]
                text_lines = self._filter_right_side(result, img_width)
            else:
                text_lines = [line[1] for line in result if line and len(line) >= 2]
            
            # 4.join text lines
            ocr_text = "\n".join(text_lines).strip()
            console.print(f"[green]OCR 识别成功 ({len(ocr_text)} 字符) 用时 {elapse:.4f} 秒[/green]")
            console.print(Panel.fit(ocr_text, title="OCR 识别内容", border_style="dim"))
            
            return ocr_text
            
        except Exception as e:
            console.print(f"[red]RapidOCR 识别失败: {e}[/red]")
            return ""

    def save_debug_image(self, img, filename="latest_ocr.png"):
        """保存用于OCR的图像到 screenshot 文件夹"""
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        screenshot_dir = os.path.join(root_dir, 'screenshot')
        
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        path = os.path.join(screenshot_dir, filename)
        img.save(path)
        return path
