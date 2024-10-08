import json
import random
from datetime import datetime, timedelta

def generate_initial_data():
    data = []
    # Session
    data.append({
        "model": "video_app.session",
        "pk": 1,
        "fields": {
            "name": "Test Session",
            "section": 2,
            "session_code": "SEC123",
            "created_by": 1,
            "created_at": "2023-10-01T00:00:00Z"
        }
    })

    # Media entries
    GRAPH_TAG_CHOICES = ['bar', 'line', 'pie', 'box', 'histogram', 'comparison']
    VARIABLE_TAG_CHOICES = [
        'gender', 'languages', 'handedness', 'eye_color', 'hair_color', 'hair_type',
        'height', 'left_foot_length', 'right_foot_length', 'longer_foot', 'index_finger',
        'ring_finger', 'longer_finger', 'arm_span', 'travel_method', 'bed_time',
        'wake_time', 'sport_activity', 'youtube', 'instagram', 'snapchat', 'facebook',
        'twitter', 'tiktok', 'twitch', 'pinterest', 'bereal', 'whatsapp', 'discord',
        'screen_time', 'pineapple_pizza', 'ice_cream', 'cats_or_dogs', 'happiness',
        'climate_change', 'reaction_time', 'memory_test'
    ]
    IMAGE_FILES = ['test1.PNG', 'test2.png', 'test3.png', 'test4.png']

    base_date = datetime(2024, 8, 23, 13, 4, 34, 389752)

    for i in range(1, 51):
        is_graph = random.choice([True, False])
        graph_tag = random.choice(GRAPH_TAG_CHOICES) if is_graph else None
        variable_tag = random.choice(VARIABLE_TAG_CHOICES) if is_graph else None

        media_entry = {
            "model": "video_app.media",
            "pk": i,
            "fields": {
                "title": f"Test Media {i}",
                "description": f"This is test media upload {i}.",
                "media_type": "image",
                "image_file": f"images/{random.choice(IMAGE_FILES)}",
                "video_file": "",
                "session": 1,
                "uploaded_at": (base_date + timedelta(minutes=i-1)).isoformat(),
                "graph_likes": 0,
                "eye_likes": 0,
                "read_likes": 0,
                "graph_tag": graph_tag,
                "is_graph": is_graph,
                "variable_tag": variable_tag,
                "submitted_password": None
            }
        }
        data.append(media_entry)

    return data

def save_initial_data(data):
    with open('video_app/fixtures/initial_data.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    initial_data = generate_initial_data()
    save_initial_data(initial_data)
    print("initial_data.json has been generated successfully.")