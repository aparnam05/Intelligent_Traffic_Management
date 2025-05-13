import sys
import torch
import torchvision.transforms as T
import cv2
import json
import numpy as np
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

# Load Model
model = fasterrcnn_resnet50_fpn(weights="COCO_V1")

# Fix box predictor issue
in_features = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = FastRCNNPredictor(in_features, 2)  # 2 classes: Background + Pothole

# Load Trained Weights
model.load_state_dict(torch.load("faster_rcnn_pothole.pth", map_location=torch.device("cpu")), strict=False)
model.eval()

# Transform
transform = T.Compose([T.ToTensor()])

# Load Image
image_path = sys.argv[1]
result_path = sys.argv[2]  # Path to save detected image
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
img_tensor = transform(image).unsqueeze(0)

# Run Inference
with torch.no_grad():
    predictions = model(img_tensor)

# Extract Data
boxes = predictions[0]["boxes"].numpy()
scores = predictions[0]["scores"].numpy()

detections = []
for i, (box, score) in enumerate(zip(boxes, scores)):
    if score > 0.5:  # Confidence threshold
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 5)
        detections.append({"box": box.tolist(), "score": score})
# Convert numpy.float32 to Python float
detections = [{"box": box.tolist(), "score": float(score)} for box, score in zip(boxes, scores) if score > 0.5]

# Save output image with bounding boxes
cv2.imwrite(result_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

# Send JSON response
print(json.dumps(detections))  # ✅ Now serializable!

