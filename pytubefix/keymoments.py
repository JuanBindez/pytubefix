# Native python imports
from datetime import timedelta
from typing import List


class KeyMomentsThumbnail:
    """Container for key moments thumbnails."""

    def __init__(self, width: int, height: int, url: str):
        self.width = width
        self.height = height
        self.url = url

    def __repr__(self):
        return f"<pytubefix.keymoments.KeyMomentThumbnail: width={self.width}, height={self.height}, url={self.url}>"


class KeyMoment:
    """Container for key moments tracks."""

    title: str
    start_seconds: int
    duration: int  # in seconds
    thumbnails: List[KeyMomentsThumbnail]

    def __init__(self, keymoment_data: dict, duration: int):
        data = keymoment_data

        self.title = data["title"]["simpleText"]
        self.start_seconds = int(data["startMillis"]) // 1000
        self.duration = duration

        thumbnails_data = data.get("thumbnailDetails", {}).get("thumbnails", [])
        self.thumbnails = [
            KeyMomentsThumbnail(
                width=thumb["width"], height=thumb["height"], url=thumb["url"]
            )
            for thumb in thumbnails_data
        ]

    @property
    def start_label(self) -> str:
        return str(timedelta(seconds=self.start_seconds))

    def __repr__(self):
        return f"<KeyMoment: {self.title} | {self.start_label}>"
