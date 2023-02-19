from .common import InfoExtractor
from ..utils import (
    int_or_none,
    traverse_obj,
)


class PodplayIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)podplay\.com/[^/]+/podcasts/[^/]+/episodes/(?P<id>[\w-]+)'

    _TESTS = [{
        'note': 'file MD5 is unstable',
        'url': 'https://www.podplay.com/no-no/podcasts/siri-og-de-gode-hjelperne-37936/episodes/karin-klouman-hani-hussein-130338946',
        'info_dict': {
            'id': '130338946',
            'display_id': 'karin-klouman-hani-hussein-130338946',
            'ext': 'mp3',
            'title': 'Karin Klouman & Hani Hussein',
            'timestamp': 1676599200,
            'upload_date': '20230217',
            'channel': 'Siri og de gode hjelperne',
            'description': 'md5:c615c06fe5200498668b03cd10fdf465',
            'duration': 2784,
            'episode': 'Episode 12',
            'episode_number': 12,
            'season': 'Season 11',
            'season_number': 11,
        },
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        page_props = self._search_nextjs_data(webpage, display_id)['props']['pageProps']
        podcast_info = page_props['podcast']
        media_info = page_props['episode']

        return {
            'id': str(media_info['id']),
            'display_id': display_id,
            'url': media_info['url'],
            'channel': podcast_info.get('title'),
            **traverse_obj(media_info, {
                'title': ('title', {str}),
                'description': ('description', {str}),
                'duration': ('duration', {int_or_none}),
                'timestamp': ('published', {int_or_none}),
                'season_number': ('season', {int_or_none}),
                'episode_number': ('episode', {int_or_none}),
            }),
        }
