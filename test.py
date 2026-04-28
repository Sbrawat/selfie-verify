# test_setup.py

import cv2
import mediapipe as mp
import face_recognition
import streamlit as st

print("All libraries imported successfully!")

# Let's test if OpenCV can access your webcam.
# '0' usually refers to your computer's default integrated camera.
print("Attempting to access the webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Cannot open webcam. Check your system privacy settings.")
else:
    print("SUCCESS: Webcam accessed! Press 'q' in the video window to close.")
    
    while True:
        # cap.read() returns a boolean (success) and the actual image frame
        success, frame = cap.read()
        
        if success:
            # Display the frame in a window named "Test"
            cv2.imshow("Test", frame)
            
            # Wait 1 millisecond for the user to press 'q'. 
            # If 'q' is pressed, break the loop.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Clean up: release the camera hardware and close all windows
cap.release()
cv2.destroyAllWindows()
print("Test complete and cleaned up.")