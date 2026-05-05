import os
import pymongo
import datetime
import numpy as np

# If we are in Docker, this environment variable will be set to 'mongodb://mongodb:27017/'
# If we are testing locally without Docker, it falls back to 'mongodb://localhost:27017/'
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = pymongo.MongoClient(MONGO_URI)

db = client["FaceAuthDB"]
users_collection = db["Users"]
logs_collection = db["SecurityLogs"]


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

# Create a new collection for security logs
logs_collection = db["SecurityLogs"]

def log_security_event(username: str, action: str, success: bool, confidence_score: float = None):
    """Records an authentication attempt for the Admin SOC dashboard."""
    log_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
        "username": username,
        "action": action, # e.g., "REGISTER" or "VERIFY"
        "success": success,
        "confidence_score": confidence_score
    }
    logs_collection.insert_one(log_entry)

def get_recent_logs(limit: int = 50):
    """Fetches the most recent security logs for the admin dashboard."""
    # Sort by timestamp descending (-1)
    logs = list(logs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
    return logs