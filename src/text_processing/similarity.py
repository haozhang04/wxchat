import difflib
import re

class TextSimilarity:
    @staticmethod
    def normalize_text(text):
        """
        标准化文本：去除所有空白字符和标点符号，只保留汉字、字母和数字。
        用于抵抗 OCR 的标点和空格抖动。
        """
        if not text: return ""
        # 移除空格、换行、制表符
        text = "".join(text.split())
        # 移除标点符号 (简单的正则，可根据需要保留)
        text = re.sub(r'[^\w\u4e00-\u9fa5]', '', text)
        return text

    @staticmethod
    def get_incremental_content(last_text, curr_text):
        """
        计算相对于 last_text 的新增内容。
        """
        if not last_text: return curr_text
        if not curr_text: return ""

        # 1. 尝试直接字面匹配 (最快)
        if curr_text.startswith(last_text):
            return curr_text[len(last_text):].strip()

        # 2. 尝试行级匹配
        last_lines = [l.strip() for l in last_text.split('\n') if l.strip()]
        curr_lines = [l.strip() for l in curr_text.split('\n') if l.strip()]
        
        if not last_lines: return curr_text
        if not curr_lines: return ""

        matcher = difflib.SequenceMatcher(None, last_lines, curr_lines)
        match = matcher.find_longest_match(0, len(last_lines), 0, len(curr_lines))
        
        # 核心逻辑：检查匹配块是否覆盖了 last_lines 的尾部
        # 允许有一定的容错（比如 last_lines 的最后一行 OCR 识别烂了，没匹配上，依然算匹配成功）
        if match.size > 0 and (match.a + match.size >= len(last_lines) - 1):
            new_lines_start_idx = match.b + match.size
            if new_lines_start_idx < len(curr_lines):
                return "\n".join(curr_lines[new_lines_start_idx:])
            else:
                return "" # 完全重叠，无新内容
        
        # 3. 如果行级匹配失败，计算整体相似度兜底
        # 如果整体相似度极高 (>90%)，认为就是同一段话（OCR 误差导致没对齐），返回空
        if matcher.ratio() > 0.9:
            return ""

        # 4. 无法匹配，认为是全新内容
        return curr_text

    @staticmethod
    def is_duplicate_message(ocr_text, last_sent_msg):
        """
        判断 OCR 内容是否包含自己刚刚发送的消息
        """
        if not ocr_text or not last_sent_msg:
            return False, ""

        # 标准化处理后再比对
        norm_ocr = TextSimilarity.normalize_text(ocr_text)
        norm_last = TextSimilarity.normalize_text(last_sent_msg)

        if not norm_ocr or not norm_last:
            return False, ""

        # 1. 包含检测 (最强硬的判断)
        if norm_last in norm_ocr:
            return True, "包含完全匹配内容(标准化后)"

        # 2. 相似度检测
        ratio = difflib.SequenceMatcher(None, norm_last, norm_ocr).ratio()
        
        # 3. 后缀检测 (防止长文截断)
        suffix_len = min(len(norm_last), 20)
        last_suffix = norm_last[-suffix_len:]
        if last_suffix in norm_ocr:
             return True, "包含消息后缀"

        if ratio > 0.85: # 建议提高阈值到 0.85
            return True, f"相似度过高 ({ratio:.2f})"

        return False, ""

    @staticmethod
    def has_trigger_keyword(text, keyword="ros"):
        """
        检查文本中是否包含触发关键词 (模糊匹配)
        使用单词边界检测，避免匹配到类似 'rose', 'prose' 等单词
        """
        if not text:
            return False
            
        # 1. 精确单词匹配 (Word Boundary)
        # re.escape 确保 keyword 中的特殊字符被转义
        # \b 匹配单词边界
        pattern = r'\b' + re.escape(keyword) + r'\b'
        
        # 使用 IGNORECASE 忽略大小写
        if re.search(pattern, text, re.IGNORECASE):
            return True
            
        return False