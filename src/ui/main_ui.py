import tkinter as tk
from tkinter import ttk
import threading
import sys
from src.core.app import GeminiApp
from config import TARGET_MODELS

class MainUI:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.root.title("Trae AI Control Panel")
        self.root.geometry("400x300")
        
        # Theme setup
        style = ttk.Style()
        style.theme_use('clam')
        
        self._init_components()
        
        # Start overlay process
        self.app.overlay_manager.start()
        self.app.overlay_manager.update_state(False, False)

    def _init_components(self):
        # Top Frame: Settings
        top_frame = ttk.LabelFrame(self.root, text="Model Settings", padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Model Selection
        ttk.Label(top_frame, text="Model:").pack(side=tk.LEFT, padx=5)
        self.model_var = tk.StringVar(value=self.app.current_model)
        self.model_combo = ttk.Combobox(top_frame, textvariable=self.model_var, values=TARGET_MODELS, width=25)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_change)
        
        # Control Frame
        ctrl_frame = ttk.LabelFrame(self.root, text="Mode Controls", padding=10)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Buttons Grid
        self.btn_edit = ttk.Button(ctrl_frame, text="Edit Regions", command=self._toggle_edit)
        self.btn_edit.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_lock = ttk.Button(ctrl_frame, text="Lock Regions", command=self._lock_regions)
        self.btn_lock.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.btn_ocr = ttk.Button(ctrl_frame, text="Toggle OCR", command=self._toggle_ocr)
        self.btn_ocr.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_autochat = ttk.Button(ctrl_frame, text="Start AutoChat", command=self._toggle_autochat)
        self.btn_autochat.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Output Button
        self.btn_output = ttk.Button(ctrl_frame, text="Output Mode", command=self._trigger_output)
        self.btn_output.grid(row=2, column=0, columnspan=1, padx=5, pady=5, sticky="ew")

        # Chat Button
        self.btn_chat = ttk.Button(ctrl_frame, text="Chat / Run", command=self._trigger_chat)
        self.btn_chat.grid(row=2, column=1, columnspan=1, padx=5, pady=5, sticky="ew")

        # Exit Button
        self.btn_exit = ttk.Button(ctrl_frame, text="Exit App", command=self._on_exit)
        self.btn_exit.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        
        # Configure grid weights
        ctrl_frame.columnconfigure(0, weight=1)
        ctrl_frame.columnconfigure(1, weight=1)

        # Status Label
        self.status_var = tk.StringVar(value="Status: IDLE")
        self.lbl_status = ttk.Label(self.root, textvariable=self.status_var, foreground="blue")
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def _on_model_change(self, event):
        model = self.model_var.get()
        self.app.set_model(model)
        
    def _toggle_edit(self):
        self.app.overlay_manager.update_state(True, self.app.ocr_enabled)
        self.status_var.set("Status: EDITING")
        print("[UI] Switched to Edit Mode")
        
    def _lock_regions(self):
        self.app.overlay_manager.update_state(False, self.app.ocr_enabled)
        self.status_var.set("Status: LOCKED")
        print("[UI] Regions Locked")
        
    def _toggle_ocr(self):
        self.app.ocr_enabled = not self.app.ocr_enabled
        state = "ON" if self.app.ocr_enabled else "OFF"
        print(f"[UI] OCR Enabled: {state}")
        self.app.overlay_manager.update_state(False, self.app.ocr_enabled)
        
    def _toggle_autochat(self):
        # 如果当前正在运行 autochat，则尝试停止
        if self.app.autochat_running:
            self.app.stop_autochat()
            self.btn_autochat.config(text="Start AutoChat")
            self.status_var.set("Status: IDLE")
            print("[UI] AutoChat stop signal sent.")
        else:
            # Send command to CLI loop
            self.app.post_command("autochat")
            # Update UI optimistically (though loop will confirm)
            self.app.autochat_running = True
            self.btn_autochat.config(text="Stop AutoChat")
            self.status_var.set("Status: AUTO_CHAT (Waiting for CLI...)")
            print("[UI] AutoChat start command sent to terminal.")
            
    def _trigger_output(self):
        self.app.post_command("output")
        print("[UI] Output command sent to terminal.")

    def _trigger_chat(self):
        self.app.post_command("chat")
        print("[UI] Chat command sent to terminal.")

    def _on_exit(self):
        # We also need to stop the app thread if possible, or let it die with the process
        # Using os._exit to force kill all threads
        
        # Stop overlay first
        self.app.overlay_manager.stop()
        
        import os
        os._exit(0)

    def run(self):
        # Start the App's CLI loop in a separate thread
        # This allows the UI to stay responsive
        cli_thread = threading.Thread(target=self.app.run, daemon=True)
        cli_thread.start()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

