from ultralytics import YOLO
import cv2
import mediapipe as mp

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Initialize webcam
cap = cv2.VideoCapture(0)  # Use 0 for webcam

# Set up MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]  # Run YOLO

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "person":
            person_crop = frame[y1:y2, x1:x2]
            image_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            result_pose = pose.process(image_rgb)

            has_helmet = False
            has_bag = False

            for item in results.boxes:
                cls2 = int(item.cls[0])
                label2 = model.names[cls2]
                bx1, by1, bx2, by2 = map(int, item.xyxy[0])

                if label2 == "backpack":
                    if bx1 < x2 and bx2 > x1:
                        has_bag = True
                elif label2 == "helmet":  # Only if using custom model that detects helmet
                    if bx1 < x2 and bx2 > x1:
                        has_helmet = True

            # Draw box
            color = (0, 255, 0) if has_helmet and has_bag else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"Helmet: {has_helmet} | Bag: {has_bag}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Helmet & Bag Detection", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

