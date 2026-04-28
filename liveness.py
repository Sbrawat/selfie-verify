import cv2
import mediapipe as mp
import time

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

cap = cv2.VideoCapture(0)
blink_count = 0
eye_closed = False

# Landmark indices for the left eye in MediaPipe
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145

while cap.isOpened():
    success, image = cap.read()
    if not success: break

    # Convert to RGB for MediaPipe
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Get specific Y-coordinates for eyelids
            top_point = face_landmarks.landmark[LEFT_EYE_TOP].y
            bottom_point = face_landmarks.landmark[LEFT_EYE_BOTTOM].y
            
            # Calculate distance
            distance = bottom_point - top_point

            # Blink Logic: Threshold is usually around 0.015 for MediaPipe
            if distance < 0.012:
                if not eye_closed:
                    blink_count += 1
                    eye_closed = True
            else:
                eye_closed = False

            cv2.putText(image, f"Blinks: {blink_count}", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow('Liveness Check', image)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()