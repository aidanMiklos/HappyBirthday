import os
import json
from video_generation import generate_video

db_path = "uploaded_videos.json"

def load_database():
    if not os.path.exists(db_path):
        return []
    with open(db_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_database(data):
    with open(db_path, "w") as file:
        json.dump(data, file, indent=4)

def is_uploaded(name, style="OG"):
    db = load_database()
    return any(entry["name"] == name and entry["birthday_style"] == style for entry in db)

def mark_uploaded(name, style="OG"):
    db = load_database()
    db.append({"name": name, "birthday_style": style})
    save_database(db)

def csv_to_array(filepath):
    names = []
    with open(filepath) as file:
        for line in file:
            names.append(line.split(',')[1].strip('\n'))
    return names

def top_names(amount, should_upload, should_schedule):
    boy_names = csv_to_array('names/boy_names_2023.csv')
    girl_names = csv_to_array('names/girl_names_2023.csv')
    
    # Combine boy and girl names and initialize an empty list to hold names to process
    all_names = boy_names + girl_names
    names_to_process = []
    
    # Loop through the combined list and add unuploaded names until the desired amount is reached
    for name in all_names:
        if not is_uploaded(name):
            names_to_process.append(name)
        if len(names_to_process) == amount:
            break
    
    # Now, process the names that need uploading
    for name in names_to_process:
        generate_video(name, should_upload, should_schedule)
        if should_upload:
            mark_uploaded(name)
            
if __name__ == "__main__":
    top_names(1, True,True)