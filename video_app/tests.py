import json
from datetime import datetime

# Function to generate media entries
def generate_media_entries(num_entries):
    media_entries = []
    for i in range(1, num_entries + 1):
        media_entry = {
            "model": "video_app.media",
            "pk": i,
            "fields": {
                "title": f"Test Media {i}",
                "description": f"This is test media upload {i}.",
                "tag": "education",
                "image_file": f"images/test2.png",
                "session": 1,
                "uploaded_at": datetime.now().isoformat()
            }
        }
        media_entries.append(media_entry)
    return media_entries

# Generate 50 media entries
media_entries = generate_media_entries(50)

# Add the session entry
session_entry = {
    "model": "video_app.session",
    "pk": 1,
    "fields": {
        "name": "Test Session",
        "section": 2,
        "session_code": "SEC123",
        "created_by": "admin",
        "created_at": "2023-10-01T00:00:00Z"
    }
}

# Combine session entry with media entries
data = [session_entry] + media_entries

# Write to JSON file
with open('video_app/fixtures/initial_data.json', 'w') as f:
    json.dump(data, f, indent=4)
