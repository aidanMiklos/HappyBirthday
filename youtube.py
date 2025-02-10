import os
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define the API service name and version
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Define the scopes required for the API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def optimize_thumbnail(thumbnail_path):
    optimized_path = "optimized_thumbnail.jpg"
    try:
        with Image.open(thumbnail_path) as img:
            img = img.convert("RGB")  # Ensure it's in JPEG format
            img.thumbnail((1280, 720))  # Resize if needed
            img.save(optimized_path, "JPEG", quality=85)  # Save with compression
        return optimized_path
    except Exception as e:
        print(f"Error optimizing thumbnail: {e}")
        return None

def generate_video_specifics(name):
    tags = [f"happy birthday {name}", f"{name} birthday","happy birthday song","happy birthday","custom happy birthday"]
    title = f"CHOIR SINGS {name.upper()} HAPPY BIRTHDAY SONG!!! (HAPPY BIRTHDAY {name.upper()})"
    description = f"THE VERY BEST CUSTOM HAPPY BIRTHDAY SONG FOR EVERY {name.upper()} ON THE PLANET!! PERFECT SONG FOR YOU OR YOUR CHILD'S BIRTHDAY 🎂🎂🎂🎂 SUNG BY CHOIR"
    return title, description, tags

def get_authenticated_service():
    # Authenticate using the service account
    credentials = service_account.Credentials.from_service_account_file(
    'client_secrets.json',
    scopes=SCOPES
    )

    # Build the API client
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    return youtube

def upload_video(name):
    title, description, tags = generate_video_specifics(name)

    youtube = get_authenticated_service()
    video_file = os.path.join("videos/", name + '_final.mp4')
    thumbnail_file = os.path.join("thumbnails/", name + '_screenshot.png')

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "10",
            },
            "status": {
                "privacyStatus": "public",
            },
        },
        media_body=googleapiclient.http.MediaFileUpload(video_file, chunksize=-1, resumable=True),
    )

    response = request.execute()
    video_id = response['id']
    print(f"Video uploaded successfully: https://www.youtube.com/watch?v={video_id}")

    # Upload thumbnail if provided
    if thumbnail_file and os.path.exists(thumbnail_file):
        optimized_thumbnail = optimize_thumbnail(thumbnail_file)
        if optimized_thumbnail:
            try:
                thumbnail_request = youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=googleapiclient.http.MediaFileUpload(optimized_thumbnail)
                )
                thumbnail_request.execute()
                print("Thumbnail uploaded successfully.")
                
            except googleapiclient.errors.HttpError as e:
                print(f"Error uploading thumbnail: {e}")

    return video_id
