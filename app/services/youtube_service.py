from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

class YouTubeService:
    def __init__(self):
        self.youtube = build(
            "youtube", "v3",
            developerKey=os.getenv("YOUTUBE_API_KEY")
        )

    def upload_video(self, file_path, title, description, tags=None):
        request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags or [],
                    "categoryId": "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": "public"
                }
            },
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        return response
