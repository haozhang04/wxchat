import tkinter as tk
from tkinter import ttk
import threading
import os
from src.core.app import App
from src.fsm import AppState
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
        self.status_var = tk.StringVar(value="Status: IDLE_STATE")
        self.lbl_status = ttk.Label(self.root, textvariable=self.status_var, foreground="blue")
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def _on_model_change(self, event):
        model = self.model_var.get()
        self.app.set_model(model)
        
    def _toggle_edit_mode(self):
        if self.app.fsm_manager.current_state_enum == AppState.EDIT_STATE:
             # Already in Edit mode, do nothing
             return
        
        self.app.post_command("edit")
        self.status_var.set("Status: EDIT_STATEING")
        
    def _trigger_ocr(self):
        if self.app.fsm_manager.current_state_enum == AppState.OCR_STATE:
             return
             
        self.app.post_command("ocr_processing")
        self.status_var.set("Status: OCR_STATE")
        
    def _toggle_autochat(self):
        if self.app.fsm_manager.current_state_enum == AppState.AUTOCHAT_STATE:
             return

        self.app.post_command("autochat")
        self.status_var.set("Status: AUTOCHAT_STATE")
        print("[UI] AutoChat start command sent.")
            
    def _trigger_output(self):
        if self.app.fsm_manager.current_state_enum == AppState.OUTPUT_STATE:
            return
        self.app.post_command("output")
        print("[UI] Output command sent to terminal.")

    def _trigger_chat(self):
        if self.app.fsm_manager.current_state_enum == AppState.IDLE_STATE:
            return
        self.app.post_command("chat")
        print("[UI] Chat command sent to terminal.")

    def _on_exit(self):
        # Stop overlay first
        self.app.overlay.stop()
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

