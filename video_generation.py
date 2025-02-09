import os
import cv2
from vidgear.gears import WriteGear
from voice_generation import generate_happy_birthday, generate_name
from moviepy import AudioFileClip, CompositeAudioClip
import subprocess
from youtube import upload_video
import shutil

def delete_all_files(directory, exceptions=None):
    """Deletes all files and subdirectories in the specified directory, except those in exceptions."""
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    if exceptions is None:
        exceptions = set()
    else:
        exceptions = set(exceptions)  # Convert to a set for faster lookups

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename in exceptions:
            continue  # Skip files or directories in the exceptions list
        
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Deletes subdirectories too
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    print(f"All files in '{directory}' (except {exceptions}) have been deleted.")

def extract_screenshot(name, video_path, timestamp=15):
    """
    Extracts a frame from a video at the specified timestamp and saves it as a PNG.
    """
    output_path = 'thumbnails/'
    os.makedirs(output_path, exist_ok=True)
    screenshot_path = os.path.join(output_path, f"{name}_screenshot.png")
    
    command = [
        "ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
        "-frames:v", "1", "-q:v", "2", "-update", "1", screenshot_path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #print("FFmpeg Output:", result.stdout)
    #print("FFmpeg Error:", result.stderr)
    print(f"Screenshot saved as {screenshot_path}")

def flashing_text(frame, name, color):
    """Overlay flashing text on a video frame."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 20  # Initial font scale
    max_width = frame.shape[1] * 0.9  # Maximum allowed text width (90% of frame width)
    thickness = 25  # Text thickness

    # Calculate text size
    text_size = cv2.getTextSize(name, font, font_scale, thickness)[0]

    # Adjust font scale if text is too wide
    while text_size[0] > max_width and font_scale > 0.1:
        font_scale -= 0.1
        text_size = cv2.getTextSize(name, font, font_scale, thickness)[0]

    # Calculate text position to center it
    text_x = int((frame.shape[1]-text_size[0])/2)  # Center horizontally
    text_y = int((frame.shape[0] + text_size[1]) / 2)  # Center vertically

    #print(frame.shape[0],frame.shape[1],text_size[0],text_size[1])

    # Overlay text on the frame
    cv2.putText(frame, name, (text_x, text_y), font, font_scale, color, thickness)

    return frame

def insert_audio_into_video(video_path, name, timestamps, happy_timestamps, output_path):
    """Insert generated audio into video at specified timestamps with flashing text."""
    audio_path = generate_name(name)
    happy_audio_path = generate_happy_birthday(name)
    if not audio_path or not happy_audio_path:
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))  # Ensure correct frame rate

    output_params = {"-vcodec": "libx264", "-pix_fmt": "yuv420p", "-crf": 18, "-preset": "ultrafast","-input_framerate": fps}
    writer = WriteGear(output=os.path.join(output_path, f"{name}.mp4"), compression_mode=True, **output_params)

    colors = [(255, 0, 255),(0, 0, 255), (0, 255, 255), (255, 0, 0), (0, 255, 0)]
    duration = AudioFileClip(audio_path).duration
    frames_per_color = int((duration / len(colors)) * fps)

    text_frames = {}
    for ts in timestamps + happy_timestamps:
        start_frame = int(ts * fps)
        end_frame = start_frame + int(1.0 * fps)
        for frame in range(start_frame, end_frame):
            text_frames[frame] = True

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count in text_frames:
            color_index = (frame_count // frames_per_color) % len(colors)
            frame = flashing_text(frame, name.upper(), colors[color_index])
        writer.write(frame)
        frame_count += 1

    cap.release()
    writer.close()

    original_audio = AudioFileClip(video_path).with_volume_scaled(0.7)
    name_audio = AudioFileClip(audio_path).with_volume_scaled(6)
    happy_audio = AudioFileClip(happy_audio_path).with_volume_scaled(6)
    final_audio = CompositeAudioClip([
        original_audio,
        *[name_audio.with_start(ts) for ts in timestamps],
        *[happy_audio.with_start(ts) for ts in happy_timestamps]
    ])

    final_audio_path = "temp_audio.aac"
    final_audio.write_audiofile(final_audio_path, codec='aac')

    merged_output_path = os.path.join(output_path, f"{name}_final.mp4")
    command = [
        "ffmpeg", "-i", os.path.join(output_path, f"{name}.mp4"), "-i", final_audio_path,
        "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", "-map", "0:v:0", "-map", "1:a:0", "-y", merged_output_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #print("FFmpeg Merge Output:", result.stdout)
    #print("FFmpeg Merge Error:", result.stderr)

    extract_screenshot(name, os.path.join(output_path, f"{name}.mp4"))
    os.remove(final_audio_path)
    os.remove(os.path.join(output_path, f"{name}.mp4"))

def generate_video(name, upload,should_schedule):
    delete_all_files('thumbnails')
    delete_all_files('videos', exceptions=['base_video.mp4'])
    video_path = "videos/base_video.mp4"
    timestamps = [6.3,15, 38.7]
    happy_timestamps = [12.2, 53]
    output_path = "videos/"
    print(f"Testing with name: {name}")
    insert_audio_into_video(video_path, name, timestamps, happy_timestamps, output_path)
    print(f"Test video saved as {os.path.join(output_path, name + '_final.mp4')}")
    if upload:
        print("Uploading video to YouTube...")
        upload_video(name)

