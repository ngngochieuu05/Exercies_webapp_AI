from ultralytics import YOLO
import os

def export_model():
    print("Loading YOLOv8 Nano Pose model...")
    # This automatically downloads 'yolov8n-pose.pt' if not present
    model = YOLO("yolov8n-pose.pt")
    
    print("Exporting model to ONNX format...")
    # Export the model
    onnx_path = model.export(format="onnx", imgsz=640, optimize=True)
    print(f"Model successfully exported to: {onnx_path}")

if __name__ == "__main__":
    export_model()
