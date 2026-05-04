# db/mongo_client.py
import pymongo
import numpy as np

# Connect to the MongoDB server
MONGO_URI = "mongodb://localhost:27017/"
client = pymongo.MongoClient(MONGO_URI)

# Create/Connect to the database and collection
db = client["FaceAuthDB"]
users_collection = db["Users"]

def create_user_profile(username, embedding, notes=""):
    """Saves a new user and their facial embedding to the database."""
    # CRITICAL: MongoDB cannot store NumPy arrays directly. 
    # We must convert the 128-d embedding into a standard Python list.
    if isinstance(embedding, np.ndarray):
        embedding = embedding.tolist()
        
    user_doc = {
        "username": username,
        "face_embedding": embedding,
        "notes": notes
    }
    
    # upsert=True means it will update the user if they exist, or create them if they don't
    users_collection.update_one(
        {"username": username}, 
        {"$set": user_doc}, 
        upsert=True
    )
    return True

def get_user_embedding(username):
    """Fetches a user's embedding and converts it back to a NumPy array for matching."""
    user = users_collection.find_one({"username": username})
    if user and "face_embedding" in user:
        # face_recognition requires NumPy arrays, so we convert it back
        return np.array(user["face_embedding"])
    return None

def save_user_notes(username, notes):
    """Updates the secure canvas notes for a specific user."""
    users_collection.update_one(
        {"username": username},
        {"$set": {"notes": notes}}
    )

def fetch_user_notes(username):
    """Retrieves the canvas notes for a specific user."""
    user = users_collection.find_one({"username": username})
    if user and "notes" in user:
        return user["notes"]
    return ""

def save_session_token(username, session_token):
    """Saves a secure session token to the user's database document."""
    users_collection.update_one(
        {"username": username},
        {"$set": {"session_token": session_token}}
    )

def get_user_by_session(session_token):
    """Looks up a user by their session token. Returns username if found."""
    user = users_collection.find_one({"session_token": session_token})
    if user:
        return user["username"]
    return None