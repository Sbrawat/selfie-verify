import face_recognition
import pickle # Used to save the "fingerprint" file

def register_face(image_path, user_name):
    # Load the image file
    image = face_recognition.load_image_file(image_path)
    
    # Generate the 128-d encoding
    # [0] because we assume there is only one face in the photo
    encoding = face_recognition.face_encodings(image)[0]
    
    # Save the encoding to a file named after the user
    with open(f"{user_name}.pkl", "wb") as f:
        pickle.dump(encoding, f)
    
    print(f"User {user_name} registered successfully!")

# Usage
# register_face("my_selfie.jpg", "Suraj_Rawat")