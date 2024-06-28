# Code to download transcripts from YouTube
import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    VideoUnavailable,
    TooManyRequests,
    YouTubeRequestFailed,
    NoTranscriptFound,
    TranscriptsDisabled,
    NotTranslatable,
    TranslationLanguageNotAvailable,
    NoTranscriptAvailable,
    FailedToCreateConsentCookie,
    InvalidVideoId,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeTranscriptFetcher:
    def __init__(self, url: str, lang: str = 'en'):
        self.url = url
        self.lang = lang
        self.video_id = self._get_video_id()

    def _get_video_id(self) -> str:
        """Extract video ID from a YouTube URL."""
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', self.url)
        if not video_id_match:
            logger.error("Invalid YouTube URL")
            raise ValueError("Invalid YouTube URL")
        return video_id_match.group(1)

    def fetch_transcript(self, text_only: bool = False) -> list:
        """Fetch and return the transcript of the given YouTube video URL."""
        if not self.video_id:
            return []
        
        try:
            transcript = YouTubeTranscriptApi.get_transcript(self.video_id, languages=[self.lang])
            if text_only:
                return self._extract_text_only(transcript)
            return transcript
        except (
            VideoUnavailable,
            TooManyRequests,
            YouTubeRequestFailed,
            NoTranscriptFound,
            TranscriptsDisabled,
            NotTranslatable,
            TranslationLanguageNotAvailable,
            NoTranscriptAvailable,
            FailedToCreateConsentCookie,
            InvalidVideoId,
        ) as e:
            logger.error(f"Failed to fetch transcript: {str(e)}")
            return []

    def _extract_text_only(self, transcript: list) -> list:
        """Extract only the text from the transcript."""
        return [entry['text'] for entry in transcript]

def print_transcript(transcript: list):
    """Print the transcript in a readable format."""
    if not transcript:
        logger.info("No transcript available.")
        return
    
    for entry in transcript:
        if isinstance(entry, dict):
            print(f"{entry['start']} - {entry['duration']}: {entry['text']}")
        else:
            print(entry)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        logger.error("Usage: python youtube_transcript.py <YouTube Video URL> <text_only> <language>")
        sys.exit(1)
    
    url = sys.argv[1]
    text_only = sys.argv[2].lower() == 'true'
    lang = sys.argv[3]
    fetcher = YouTubeTranscriptFetcher(url, lang)
    transcript = fetcher.fetch_transcript(text_only=text_only)
    print_transcript(transcript)
