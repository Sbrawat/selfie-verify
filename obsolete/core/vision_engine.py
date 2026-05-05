import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import face_recognition

# Constants
LEFT_EYE_TOP, LEFT_EYE_BOTTOM = 159, 145

class VisionEngine:
    def __init__(self):
        """Initializes the MediaPipe models upon creation."""
        model_path = './models/face_landmarker.task'

        try:
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE,
                num_faces=1
            )
            self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
        except Exception as e:
            print(f"CRITICAL: Failed to load MediaPipe model at {model_path}")
            raise e

    def calculate_ear(self, face_landmarks):
        """Calculates the Eye Aspect Ratio for blink detection."""
        top_point = face_landmarks[LEFT_EYE_TOP].y
        bottom_point = face_landmarks[LEFT_EYE_BOTTOM].y
        return bottom_point - top_point

    def check_liveness(self, rgb_frame):
        """Processes a frame to detect if an eye is closed."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        results = self.face_landmarker.detect(mp_image)
        
        if results.face_landmarks:
            face_landmarks = results.face_landmarks[0]
            ear = self.calculate_ear(face_landmarks)
            return ear < 0.012 # Returns True if eye is currently closed
        return False

    def extract_embedding(self, rgb_frame):
        """Finds a face in the frame and returns its 128-d embedding."""
        face_locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if len(encodings) > 0:
            return encodings[0]
        return None

    def verify_match(self, live_encoding, saved_encoding, tolerance=0.5):
        """Compares two embeddings. Returns True if they match."""
        matches = face_recognition.compare_faces([saved_encoding], live_encoding, tolerance=tolerance)
        return matches[0]

# Instantiate a single global engine to be used by the app
engine = VisionEngine()