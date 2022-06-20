import re

from .common import InfoExtractor
from ..utils import (
    int_or_none,
    parse_iso8601,
    str_or_none,
    url_or_none,
)
from ..utils.traversal import require, traverse_obj

# So here's what happens:
# [RadioplayPodcastRedirect] Extracting URL: https://radioplay.se/podcast/lilla-my/id-2001126/play/
# [RadioplayPodcastRedirect] 2001126: Downloading webpage
# [Listennow] Extracting URL: https://radioplay.listennow.link/5507717
# [Listennow] 5507717: Downloading webpage
# [RadioplayPodcast] Extracting URL: https://radioplay.se/podcast/lilla-my/lyssna/2001126/
# [RadioplayPodcast] 2001126: Downloading webpage


class RadioplayRedirectIE(InfoExtractor):
    _VALID_URL = r'https?://(?:live|lytte)\.radioplay\.(?:se|no|dk)/(?P<id>\d+)'

    _TESTS = [{
        'url': 'https://lytte.radioplay.no/10279674',
        'info_dict': {
            'id': '10030542',
            'display_id': '2035659',
            'ext': 'mp3',
            'title': 'Best of Høsten 2020',
            'description': 'md5:ea1af250826e1875931754fbdf51aa53',
            'timestamp': 1603429200,
            'upload_date': '20201023',
            'duration': 4182,
            'season_number': 6,
            'season': str,
            'channel': 'Siri og de gode hjelperne',
            'thumbnail': r're:https?://.*',
        },
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        url = self._search_regex(
            r'desktopUrl\s*:\s*\'([^\']+)\'', webpage,
            'redirect', video_id)
        return self.url_result(url)


class RadioplayIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?radioplay\.(?:se|no|dk)/(?:[^/]+/)+(?:id-)?(?P<id>[^/?#]+)'

    _TESTS = [{
        'note': 'podcast link type 1',
        'url': 'https://radioplay.no/podcast/staopp/id-2052154/',
        'info_dict': {
            'id': '10062967',
            'display_id': '2052154',
            'ext': 'mp3',
            'title': 'Episode 68 - Mossias og Jeg sa det til hun',
            'description': 'md5:fb79502f7faed090e154d40356e4a5c7',
            'timestamp': 1630126800,
            'upload_date': '20210828',
            'duration': 1851,
            'season_number': 3,
            'season': str,
            'channel': 'Stå Opp på Radio Rock',
            'thumbnail': r're:^https://planet-radio-studio-podplay\.imgix\.net/img/.*\.png',
        },
    }, {
        'note': 'podcast link type 2',
        'url': 'https://radioplay.se/podcast/lilla-my/lyssna/2001126',
        'info_dict': {
            'id': '10027569',
            'display_id': '2001126',
            'ext': 'mp3',
            'title': 'Kaktus till läraren',
            'description': 'Lilla My ska köpa en "blomma" till sin lärare.',
            'timestamp': 1549898100,
            'upload_date': '20190211',
            'duration': 114,
            'channel': 'Lilla My',
            'thumbnail': r're:^https://planet-radio-studio-podplay\.imgix\.net/img/.*\.png',
        },
    }, {
        'note': 'radio player',
        'url': 'https://radioplay.no/radio-rock/spiller/235678793/',
        'info_dict': {
            'id': '235678793',
            'display_id': '235678793',
            'ext': 'mp3',
            'title': 'The Trooper - Gammal Maiden Spessial',
            'description': 'md5:7b55cc21479518fb9f84c4fdb5233f5d',
            'timestamp': 1770681600,
            'upload_date': '20260210',
            'duration': 1800,
            'thumbnail': r're:^https://media\.bauerradio\.com/.*\.jpg',
        },
    }, {
        'note': 'redirect loop, possibly due to login requested',
        'url': 'https://radioplay.no/radio-norge/spiller/235471551/',
        'only_matching': True,
    }]

    def _extract_player(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        nextdata = self._search_nextjs_data(webpage, display_id)
        video_info = nextdata['props']['initialState']['audibles']['data'][0]

        return (
            display_id,
            video_info,
        )

    def _real_extract(self, url):
        display_id, video_info = self._extract_player(url)

        return {
            'display_id': display_id,
            **traverse_obj(video_info, {
                'id': ('id', {str_or_none}, {require('ID')}),
                'url': (('mediaUrl', 'mediaUrl_mp3'), {url_or_none}, any),
                'title': ('title', {str_or_none}),
                'description': ('description', {str}),
                'season_number': ('seasonNumber', {int_or_none}),
                'thumbnail': ('image', {str}),
                'timestamp': ('published_at', {parse_iso8601(delimiter=' ')}),
                'duration': ('duration', {int_or_none}),
                'channel': ('showTitle', {str}),
            }),
        }


class RadioplayPodcastRedirectIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?radioplay\.(?:se|no|dk)/podcast/[^/]+/id-(?P<id>\d+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        for url in re.findall(r'<div[^>]* data-test="audible-now-playing-button-container"[^>]*>[^<]*<a href="([^"]+)"', webpage):
            return self.url_result(url)
