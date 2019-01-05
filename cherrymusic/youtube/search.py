import dataclasses
import re
import requests
from dataclasses import dataclass
from urllib.parse import urlencode

from utils.jsextract import get_js_object_as_dict_after_marker


@dataclass
class YoutubeSearchResult:
    youtube_id: str
    thumbnail_url: str
    title: str
    views: int
    duration: str

    def asdict(self):
        return dataclasses.asdict(self)


def video_data_to_search_result(video_data):
    return YoutubeSearchResult(
        youtube_id=video_data['videoRenderer']['videoId'],
        thumbnail_url=video_data['videoRenderer']['thumbnail']['thumbnails'][0]['url'],
        title=video_data['videoRenderer']['title']['simpleText'],
        duration=video_data['videoRenderer']['lengthText']['simpleText'],
        views=int(re.sub('\D', '', video_data['videoRenderer']['viewCountText']['simpleText'])),
    )


def youtube_search(query):
    youtube_seach_url = 'https://www.youtube.com/results?'
    url = youtube_seach_url + urlencode({'search_query': query})
    resp = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
    })
    js_obj = get_js_object_as_dict_after_marker('window["ytInitialData"] = ', resp.text)
    videos = js_obj['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    return [
        video_data_to_search_result(video)
        for video in videos
        if 'videoRenderer' in video  # do not parse playlists
    ]