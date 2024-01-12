from .common import InfoExtractor


class FilmarchivesJpIE(InfoExtractor):
    IE_NAME = 'filmarchives.jp'
    _VALID_URL = r'https?://animation\.filmarchives\.jp/(?:(?P<site_lang>(?:en)?)/)?works/play(?P<video_lang>[^/]*)/(?P<id>[^/?#]+)'
    # FIXME we should support the top-level pages ('view/'), such as https://animation.filmarchives.jp/en/works/view/44405
    # and select the video language from the site language

    _TESTS = [{
        'url': 'https://animation.filmarchives.jp/en/works/playen/41061',
        # no MD5, the first fragment is too small
        'info_dict': {
            'id': '41061-1_en-en',
            'display_id': '41061',
            'title': 'The Story of the Monkey King | Animation | Japanese Animated Film Classics',
            'ext': 'mp4',
            'description': 'md5:f1b0ece457899326329b6eeca7a1909e',
            'thumbnail': 'http://h10.cs.nii.ac.jp/stream/nfc/4106102_en/poster.png',
            '_old_archive_ids': ['generic 41061'],
        },
    }, {
        'url': 'https://animation.filmarchives.jp/works/play/41061',
        # no MD5, the first fragment is too small
        'info_dict': {
            'id': '41061-1_jp-jp',
            'display_id': '41061',
            'title': '切紙細工 西遊記 孫悟空物語 | 作品動画 | 日本アニメーション映画クラシックス',
            'ext': 'mp4',
            'description': 'md5:2cd391ed96b56672c12d078b8a1eaab2',
            'thumbnail': 'http://h10.cs.nii.ac.jp/stream/nfc/4106102_jp/poster.png',
            '_old_archive_ids': ['generic 41061'],
        },
    }]

    def _real_extract(self, url):
        video_id, video_lang, site_lang = self._match_valid_url(url).group('id', 'video_lang', 'site_lang')
        if site_lang is None or site_lang == '':
            site_lang = 'jp'
        if video_lang == '':
            video_lang = 'jp'
        webpage = self._download_webpage(url, video_id)

        iframe_url = self._search_regex(
            r'<iframe\b[^>]+\bsrc\s*=\s*(["\'])(?P<url>.*?)\1', webpage, 'iframe URL', group='url')
        iframe = self._download_webpage(iframe_url, video_id)

        # this returns a list of info dicts
        embeds = self._extract_generic_embeds(url, iframe)
        info_dict = embeds[0]  # HACK, take only the first one
        # the English and the original Japanese URLs result in different
        # metadata, and there are subtitled videos with the same 'id's, so
        # modify the 'id's to be unique
        info_dict['id'] = info_dict['id'] + '_' + site_lang + '-' + video_lang
        info_dict['display_id'] = video_id
        info_dict['title'] = self._og_search_title(webpage) or info_dict['title']
        info_dict['description'] = self._og_search_description(webpage) or info_dict['description']

        return info_dict
