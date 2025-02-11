import os
import google.auth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from PIL import Image

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

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
    tags = [f"happy birthday {name}", f"{name} birthday", "happy birthday song", "happy birthday", "custom happy birthday"]
    title = f"CHOIR SINGS {name.upper()} HAPPY BIRTHDAY SONG!!! (HAPPY BIRTHDAY {name.upper()})"
    description = f"THE VERY BEST CUSTOM HAPPY BIRTHDAY SONG FOR EVERY {name.upper()} ON THE PLANET!! PERFECT SONG FOR YOU OR YOUR CHILD'S BIRTHDAY 🎂🎂🎂🎂 SUNG BY CHOIR"
    return title, description, tags

def get_authenticated_service():
    credentials = Credentials(
        None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES,
    )

    if not credentials.valid:
        credentials.refresh(google.auth.transport.requests.Request())

    return build("youtube", "v3", credentials=credentials)

def upload_video(name):
    title, description, tags = generate_video_specifics(name)

    youtube = get_authenticated_service()
    video_file = os.path.join("videos/", name + '_final.mp4')
    thumbnail_file = os.path.join("thumbnails/", name + '_screenshot.png')

    try:
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
            media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True),
        )

        response = request.execute()
        video_id = response['id']
        print(f"Video uploaded successfully: https://www.youtube.com/watch?v={video_id}")

        if thumbnail_file and os.path.exists(thumbnail_file):
            optimized_thumbnail = optimize_thumbnail(thumbnail_file)
            if optimized_thumbnail:
                try:
                    thumbnail_request = youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaFileUpload(optimized_thumbnail)
                    )
                    thumbnail_request.execute()
                    print("Thumbnail uploaded successfully.")
                except HttpError as e:
                    print(f"Error uploading thumbnail: {e}")

        return video_id

    except HttpError as e:
        print(f"An error occurred: {e}")
        return None
