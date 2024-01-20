from firebase_admin import storage
from firebase.firebase_app import getFirebaseApp

app = getFirebaseApp()

def save_creator_sample(email: str, mp3_file: bytes):
  # Get the default storage bucket for the Firebase app
  bucket = storage.bucket('audio_samples', app=app)
    # Set the storage path for the MP3 file
  storage_path = f'{email}/samples/sample.mp3'
    # Create a blob object that points to the storage path
  blob = bucket.blob(storage_path)
    # Upload the MP3 file data to the blob
  blob.upload_from_string(mp3_file, content_type='audio/mp3')
    # Return the public URL of the uploaded file
  return blob.public_url
