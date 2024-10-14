import os
from django.conf import settings

def get_available_character_sets():
    """Get a list of available character set names."""
    character_dir = os.path.join(settings.BASE_DIR, 'video_app', 'static', 'video_app', 'characters')
    return [os.path.splitext(f)[0] for f in os.listdir(character_dir) if f.endswith('.csv')]