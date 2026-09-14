import re
from urllib.parse import urlparse, parse_qs
from django.core.exceptions import ValidationError

def youtube_video_id(value):
    if not value: return ''
    parsed = urlparse(value)
    host = (parsed.hostname or '').lower()
    video_id = ''
    if parsed.scheme in ('https', 'http') and not parsed.username and not parsed.password:
        parts = parsed.path.strip('/').split('/')
        if host == 'youtu.be' and len(parts) == 1:
            video_id = parts[0]
        elif host in ('youtube.com','www.youtube.com','m.youtube.com','youtube-nocookie.com','www.youtube-nocookie.com'):
            if parsed.path == '/watch': video_id = parse_qs(parsed.query).get('v',[''])[0]
            elif len(parts) == 2 and parts[0] in ('embed','shorts','live'): video_id = parts[1]
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}',video_id):
        raise ValidationError('Paste a valid YouTube video link, such as https://www.youtube.com/watch?v=Way9Dexny3w or https://youtu.be/Way9Dexny3w.')
    return video_id

def validate_youtube_url(value):
    youtube_video_id(value)
