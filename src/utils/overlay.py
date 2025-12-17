import tkinter as tk
import multiprocessing
import termcolor
from .screen_region_config import ScreenRegionConfig

# =============================================================================
# 1. 覆盖层控制器
# =============================================================================
class Overlay:
    def __init__(self):
        self.process = None
        self.parent_conn, self.child_conn = None, None
        self.config_manager = ScreenRegionConfig()
        self.regions = self.config_manager.load() 

    def add_region(self, key, color, label):
        """
        [接口] 添加一个监控区域。
        逻辑：必须从配置文件读取坐标。如果没有，则报错并使用默认位置提示用户调整。
        """
        # 检查是否已有保存的坐标
        saved_rect = None
        if key in self.regions:
            val = self.regions[key]
            if isinstance(val, dict) and "rect" in val:
                saved_rect = val["rect"]
            elif isinstance(val, list) and len(val) == 4:
                saved_rect = val
        
        if not saved_rect:
            termcolor.cprint(f"[Overlay] 错误: 区域 '{key}' 未在配置中找到！请使用 'edit' 模式重新框选。", "red")
            # 使用一个显眼的默认位置，以便用户可以找到并调整它
            saved_rect = [100, 100, 200, 100]

        # 构造数据
        region_data = {
            "rect": saved_rect,
            "color": color, 
            "label": label
        }
        
        self.regions[key] = region_data

        # 如果 GUI 已经在运行，实时发送更新
        if self.is_running():
            self.send_command("update_region", {"key": key, "data": region_data})

    def remove_region(self, key):
        """[接口] 删除区域"""
        if key in self.regions:
            del self.regions[key]
            # 同时更新磁盘配置，防止下次启动还存在
            self.config_manager.save(self.regions)
            
        if self.is_running():
            self.send_command("remove_region", {"key": key})

    def start(self):
        """启动 GUI 子进程"""
        if self.is_running():
            return

        self.parent_conn, self.child_conn = multiprocessing.Pipe()
        
        # 启动进程，传入当前的配置数据
        self.process = multiprocessing.Process(
            target=self._gui_process_entry,
            args=(self.child_conn, self.regions)
        )
        self.process.daemon = True
        self.process.start()
        termcolor.cprint(f"[Overlay] Started GUI process (PID: {self.process.pid})", "cyan")

    def stop(self):
        """关闭 GUI"""
        if self.is_running():
            self.send_command("quit")
            self.process.join(timeout=1)
            if self.process.is_alive():
                self.process.terminate()
            self.process = None
            termcolor.cprint("[Overlay] Stopped.", "cyan")

    def toggle_edit(self, enabled: bool):
        """[接口] 切换编辑模式"""
        self.send_command("toggle_edit", enabled)

    def update_state(self, editing: bool, ocr_enabled: bool, visible_regions: list = None):
        """
        [接口] 更新状态
        :param editing: 是否开启编辑模式
        :param ocr_enabled: (未使用，保留接口兼容)
        :param visible_regions: 可见区域列表 (None 表示全部可见)
        """
        self.send_command("update_state", {
            "editing": editing,
            "visible_regions": visible_regions
        })

    def reload_config(self):
        """[接口] 重新加载配置文件"""
        new_regions = self.config_manager.load()
        
        for key, val in new_regions.items():
            if key not in self.regions:
                continue
                
            new_rect = None
            if isinstance(val, dict) and "rect" in val:
                new_rect = val["rect"]
            elif isinstance(val, list) and len(val) == 4:
                new_rect = val
            
            if new_rect:
                self.regions[key]["rect"] = new_rect

    def get_region_rect(self, key):
        """[接口] 获取指定区域的坐标 [x, y, w, h]"""
        if key in self.regions:
            return self.regions[key]["rect"]
        return None

    def is_running(self):
        return self.process is not None and self.process.is_alive()

    def send_command(self, cmd, payload=None):
        if self.parent_conn:
            try:
                self.parent_conn.send({"cmd": cmd, "payload": payload})
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # 静态方法：GUI 子进程入口
    # -------------------------------------------------------------------------
    @staticmethod
    def _gui_process_entry(pipe_conn, initial_regions):
        app = OverlayApp(pipe_conn, initial_regions)
        app.mainloop()


# =============================================================================
# 2. GUI 实现 (运行在子进程)
# =============================================================================
class OverlayApp(tk.Tk):
    def __init__(self, pipe_conn, regions):
        super().__init__()
        self.pipe_conn = pipe_conn
        self.regions = regions
        
        # 在子进程中也实例化一个 Config 对象，用于保存
        self.config_manager = ScreenRegionConfig()
        
        self.edit_mode = True 
        self.visible_regions = None # None means all visible
        
        # 窗口设置
        self.title("Overlay")
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "black")
        self.configure(bg="black")
        
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.drag_data = {"item": None, "action": None}
        
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.check_pipe()
        self.draw_ui()

    def check_pipe(self):
        """监听主进程指令"""
        while self.pipe_conn.poll():
            try:
                msg = self.pipe_conn.recv()
                cmd = msg.get("cmd")
                payload = msg.get("payload")

                if cmd == "quit":
                    self.destroy()
                    return
                elif cmd == "update_region":
                    self.regions[payload["key"]] = payload["data"]
                    self.draw_ui()
                elif cmd == "remove_region":
                    if payload["key"] in self.regions:
                        del self.regions[payload["key"]]
                    self.draw_ui()
                elif cmd == "toggle_edit":
                    self.edit_mode = payload
                    self.draw_ui()
                elif cmd == "update_state":
                    # payload: {"editing": bool, "visible_regions": list|None}
                    self.edit_mode = payload.get("editing", False)
                    self.visible_regions = payload.get("visible_regions")
                    self.draw_ui()
            except EOFError:
                break
        self.after(50, self.check_pipe)

    def draw_ui(self):
        self.canvas.delete("all")
        dash = (4, 4) if self.edit_mode else None
        
        for key, data in self.regions.items():
            # Visibility check
            if self.visible_regions is not None and key not in self.visible_regions:
                continue

            x, y, w, h = data["rect"]
            color = data["color"]
            label = data["label"]

            # 矩形
            self.canvas.create_rectangle(
                x, y, x+w, y+h, 
                outline=color, width=2, dash=dash,
                tags=("region", key, "rect")
            )
            # 标签
            self.canvas.create_text(
                x, y-5, text=label, fill=color, anchor="sw",
                font=("Arial", 10, "bold"), tags=("region", key, "label")
            )
            # 手柄
            if self.edit_mode:
                sz = 8
                handles = [(x, y, "nw"), (x+w, y, "ne"), (x+w, y+h, "se"), (x, y+h, "sw")]
                for hx, hy, cursor in handles:
                    self.canvas.create_rectangle(
                        hx-sz//2, hy-sz//2, hx+sz//2, hy+sz//2,
                        fill=color, outline="white",
                        tags=("region", key, "handle", cursor)
                    )

    def on_press(self, event):
        if not self.edit_mode: return
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        if "region" not in tags: return
        
        self.drag_data["key"] = tags[1]
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        if "handle" in tags:
            self.drag_data["action"] = "resize"
            self.drag_data["handle"] = tags[3]
        elif "rect" in tags:
            self.drag_data["action"] = "move"

    def on_drag(self, event):
        if not self.drag_data.get("action"): return
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        key = self.drag_data["key"]
        x, y, w, h = self.regions[key]["rect"]
        
        if self.drag_data["action"] == "move":
            x += dx; y += dy
        elif self.drag_data["action"] == "resize":
            htype = self.drag_data["handle"]
            if "w" in htype: x += dx; w -= dx
            if "e" in htype: w += dx
            if "n" in htype: y += dy; h -= dy
            if "s" in htype: h += dy
            w = max(20, w); h = max(20, h)

        self.regions[key]["rect"] = [int(x), int(y), int(w), int(h)]
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.draw_ui()

    def on_release(self, event):
        if self.drag_data.get("action"):
            # 拖拽结束：直接调用你的 Config 类保存
            self.config_manager.save(self.regions)
            self.drag_data["action"] = None