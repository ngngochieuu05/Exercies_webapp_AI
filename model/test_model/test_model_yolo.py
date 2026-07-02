import os
import cv2
import threading
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from ultralytics import YOLO

# Set appearance mode and color theme for premium dark-mode look
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YoloCustomApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("YOLOv8 Pose Estimation Tester - CustomTkinter UI")
        self.geometry("1100x720")
        
        # State variables
        self.model = None
        self.cap = None
        self.is_running = False
        self.video_thread = None
        self.conf_threshold = 0.50
        self.model_dir = "D:/Python/Exercies_webapp_AI/model"
        
        # Build UI layout
        self.setup_ui()
        
        # Auto-load default model
        self.auto_load_default_model()

    def setup_ui(self):
        # Configure Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 1. Left Sidebar Frame (Controls)
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(9, weight=1)
        
        # Title/Logo
        logo_label = ctk.CTkLabel(self.sidebar_frame, text="YOLOv8 POSE", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        subtitle_label = ctk.CTkLabel(self.sidebar_frame, text="CustomTkinter Model Tester", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Model Selection
        label_model = ctk.CTkLabel(self.sidebar_frame, text="1. Chọn Mô Hình (Model):", anchor="w")
        label_model.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.model_var = ctk.StringVar()
        self.model_option = ctk.CTkOptionMenu(self.sidebar_frame, variable=self.model_var, width=220)
        self.model_option.grid(row=3, column=0, padx=20, pady=5)
        self.refresh_model_list()
        
        btn_browse_model = ctk.CTkButton(self.sidebar_frame, text="Tìm File Model Khác...", fg_color="transparent", border_width=1, command=self.browse_model)
        btn_browse_model.grid(row=4, column=0, padx=20, pady=5)
        
        # Input Source
        label_input = ctk.CTkLabel(self.sidebar_frame, text="2. Nguồn Đầu Vào (Input):", anchor="w")
        label_input.grid(row=5, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.source_var = ctk.StringVar(value="webcam")
        
        self.rb_webcam = ctk.CTkRadioButton(self.sidebar_frame, text="Camera / Webcam (0)", variable=self.source_var, value="webcam")
        self.rb_webcam.grid(row=6, column=0, padx=30, pady=5, sticky="w")
        
        self.rb_video = ctk.CTkRadioButton(self.sidebar_frame, text="Tệp Video (File)", variable=self.source_var, value="video")
        self.rb_video.grid(row=7, column=0, padx=30, pady=5, sticky="w")
        
        self.video_path_var = ctk.StringVar(value="Chưa chọn video...")
        self.lbl_video_path = ctk.CTkLabel(self.sidebar_frame, textvariable=self.video_path_var, font=ctk.CTkFont(size=11), text_color="gray", wraplength=220)
        self.lbl_video_path.grid(row=8, column=0, padx=30, pady=2, sticky="w")
        
        btn_browse_video = ctk.CTkButton(self.sidebar_frame, text="Chọn Tệp Video...", command=self.browse_video)
        btn_browse_video.grid(row=9, column=0, padx=20, pady=(5, 15), sticky="n")
        
        # Confidence slider
        self.conf_lbl_var = ctk.StringVar(value="Conf: 0.50")
        label_conf = ctk.CTkLabel(self.sidebar_frame, textvariable=self.conf_lbl_var, anchor="w")
        label_conf.grid(row=10, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.slider_conf = ctk.CTkSlider(self.sidebar_frame, from_=0.01, to=1.00, number_of_steps=100, command=self.on_conf_change)
        self.slider_conf.set(0.50)
        self.slider_conf.grid(row=11, column=0, padx=20, pady=5)
        
        # Run Controls
        self.btn_start = ctk.CTkButton(self.sidebar_frame, text="Bắt Đầu (Start)", fg_color="#1f77b4", hover_color="#155d8b", command=self.start_processing)
        self.btn_start.grid(row=12, column=0, padx=20, pady=(20, 5))
        
        self.btn_stop = ctk.CTkButton(self.sidebar_frame, text="Dừng Lại (Stop)", fg_color="#d62728", hover_color="#a81c1c", command=self.stop_processing, state="disabled")
        self.btn_stop.grid(row=13, column=0, padx=20, pady=(5, 20))

        # 2. Right Main Panel (Screen and Status)
        self.main_panel = ctk.CTkFrame(self, corner_radius=10)
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_panel.grid_columnconfigure(0, weight=1)
        self.main_panel.grid_rowconfigure(0, weight=1)
        
        # Screen Output Container
        self.screen_frame = ctk.CTkFrame(self.main_panel, fg_color="black", corner_radius=8)
        self.screen_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.screen_frame.grid_columnconfigure(0, weight=1)
        self.screen_frame.grid_rowconfigure(0, weight=1)
        
        self.video_label = ctk.CTkLabel(self.screen_frame, text="Nhấn Start để khởi chạy Video", font=ctk.CTkFont(size=14))
        self.video_label.grid(row=0, column=0, sticky="center")
        
        # Status Bar
        self.status_var = ctk.StringVar(value="Trạng thái: Sẵn sàng")
        self.status_bar = ctk.CTkLabel(self.main_panel, textvariable=self.status_var, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 10))

    def refresh_model_list(self):
        models = []
        if os.path.exists(self.model_dir):
            for file in os.listdir(self.model_dir):
                if file.endswith((".pt", ".onnx")):
                    models.append(file)
        
        if models:
            self.model_option.configure(values=models)
            self.model_var.set(models[0])
        else:
            self.model_option.configure(values=["Không tìm thấy model"])
            self.model_var.set("Không tìm thấy model")

    def auto_load_default_model(self):
        models = self.model_option.cget("values")
        if models and models[0] != "Không tìm thấy model":
            # Autoselect ONNX model if present
            for m in models:
                if m.endswith(".onnx"):
                    self.model_var.set(m)
                    break

    def browse_model(self):
        file_path = filedialog.askopenfilename(
            title="Chọn File Model YOLO",
            filetypes=[("YOLO Models", "*.pt *.onnx"), ("All files", "*.*")]
        )
        if file_path:
            self.model_dir = os.path.dirname(file_path)
            self.refresh_model_list()
            self.model_var.set(os.path.basename(file_path))

    def browse_video(self):
        file_path = filedialog.askopenfilename(
            title="Chọn File Video",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if file_path:
            self.video_path_var.set(file_path)
            self.source_var.set("video")

    def on_conf_change(self, val):
        self.conf_threshold = float(val)
        self.conf_lbl_var.set(f"Conf: {self.conf_threshold:.2f}")

    def show_placeholder(self):
        self.video_label.configure(image=None, text="Nhấn Start để khởi chạy Video")

    def start_processing(self):
        model_name = self.model_var.get()
        if not model_name or model_name == "Không tìm thấy model":
            self.status_var.set("Lỗi: Chưa chọn model!")
            return
            
        model_path = os.path.join(self.model_dir, model_name)
        if not os.path.exists(model_path):
            self.status_var.set("Lỗi: File model không tồn tại!")
            return

        self.status_var.set("Đang nạp mô hình...")
        self.update()
        
        try:
            # Load YOLO model
            self.model = YOLO(model_path)
        except Exception as e:
            self.status_var.set(f"Lỗi nạp model: {str(e)[:40]}")
            return
            
        # Determine Input Source
        source = self.source_var.get()
        if source == "webcam":
            self.cap = cv2.VideoCapture(0)
        else:
            video_file = self.video_path_var.get()
            if not os.path.exists(video_file):
                self.status_var.set("Lỗi: Không tìm thấy file video!")
                return
            self.cap = cv2.VideoCapture(video_file)

        if not self.cap.isOpened():
            self.status_var.set("Lỗi: Không mở được nguồn video!")
            return
            
        self.is_running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.model_option.configure(state="disabled")
        self.rb_webcam.configure(state="disabled")
        self.rb_video.configure(state="disabled")
        self.status_var.set("Trạng thái: Đang chạy xử lý...")
        
        # Start background video thread
        self.video_thread = threading.Thread(target=self.process_video)
        self.video_thread.daemon = True
        self.video_thread.start()

    def process_video(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                if self.source_var.get() == "video":
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break
            
            # Run YOLO Pose model
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            
            # Annotate Pose keypoints on the image
            annotated_frame = results[0].plot()
            
            # Convert frame format
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            
            # Frame dimensions
            h, w, _ = rgb_frame.shape
            target_w = 640
            target_h = int((h / w) * target_w)
            
            pil_img = Image.fromarray(rgb_frame)
            
            # Render using CTkImage (Handles scaling correctly)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_w, target_h))
            
            # Update GUI safely in main loop
            self.video_label.configure(image=ctk_img, text="")
            
        # Release capture
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.after(0, self.on_stopped)

    def on_stopped(self):
        self.show_placeholder()
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.model_option.configure(state="normal")
        self.rb_webcam.configure(state="normal")
        self.rb_video.configure(state="normal")
        self.status_var.set("Trạng thái: Đã dừng")

    def stop_processing(self):
        self.status_var.set("Đang dừng...")
        self.is_running = False

if __name__ == "__main__":
    app = YoloCustomApp()
    app.mainloop()
