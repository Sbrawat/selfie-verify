import cv2
import face_recognition

# 1. Initialize the webcam
video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # 2. Resize frame for faster processing (optional but recommended)
    # We shrink it to 1/4 size so the computer has fewer pixels to analyze
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    
    # 3. Convert image from BGR (OpenCV default) to RGB (Face_recognition default)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # 4. Find all face locations in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)

    # 5. Display the results (Drawing the box)
    for (top, right, bottom, left) in face_locations:
        # Scale back up because we detected on a 1/4 size image
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face using OpenCV
        # (Image, Start_Point, End_Point, Color_BGR, Thickness)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Display the resulting image
    cv2.imshow('Face Detection', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()