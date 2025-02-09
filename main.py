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
    
    for i in range(amount):
        cur_boy = boy_names[i]
        if not is_uploaded(cur_boy):
            generate_video(cur_boy, should_upload,should_schedule)
            if(should_upload):
                mark_uploaded(cur_boy)
        
        cur_girl = girl_names[i]
        if not is_uploaded(cur_girl):
            generate_video(cur_girl, should_upload,should_schedule)
            if(should_upload):
                mark_uploaded(cur_girl)

if __name__ == "__main__":
    top_names(50, True,True)