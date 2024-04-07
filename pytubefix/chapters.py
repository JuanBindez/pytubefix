# Native python imports
from datetime import timedelta
from typing import List


class ChapterThumbnail:
    """Container for chapter thumbnails."""

    def __init__(self, width: int, height: int, url: str):
        self.width = width
        self.height = height
        self.url = url

    def __repr__(self):
        return f'<pytubefix.chapters.ChapterThumbnail: width={self.width}, height={self.height}, url={self.url}>'


class Chapter:
    """Container for chapters tracks."""
    title: str
    start_seconds: int
    duration: int  # in seconds
    thumbnails: List[ChapterThumbnail]

    def __init__(self, chapter_data: dict, duration: int):
        data = chapter_data['chapterRenderer']

        self.title = data['title']['simpleText']
        self.start_seconds = int(data['timeRangeStartMillis'] / 1000)
        self.duration = duration

        thumbnails_data = data.get('thumbnail', {}).get('thumbnails', [])
        self.thumbnails = [
            ChapterThumbnail(
                width=thumb['width'],
                height=thumb['height'],
                url=thumb['url']
            )
            for thumb in thumbnails_data
        ]

    @property
    def start_label(self) -> str:
        return str(timedelta(seconds=self.start_seconds))

    def __repr__(self):
        return f'<Chapter: {self.title} | {self.start_label}>'
