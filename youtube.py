import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from PIL import Image
import pickle

TOKEN_FILE = "token.pickle"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"

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
    credentials = None

    # Load the stored token if it exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)

    # If credentials are not valid or don't exist, get new ones
    if not credentials or not credentials.valid:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES
        )
        credentials = flow.run_local_server(port=8080)

        # Save the credentials for next time
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

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
