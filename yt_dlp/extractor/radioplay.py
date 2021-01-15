# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor

from ..utils import (
    int_or_none,
    js_to_json,
    parse_iso8601,
    unified_strdate,
)


class RadioplayIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?radioplay\.(?:se|no)/[^/]+/spiller/(?P<id>\d+)/?'

    _TEST = {
        'url': 'https://radioplay.no/radio-rock/spiller/146818938/',
        'info_dict': {
            'id': '146818938',
            'ext': 'mp3',
            'title': 'Radio Rock LIVE - med Stein Johnsen',
            'timestamp': 1610733600,
            'upload_date': '20210115',
        },
    }

    def _extract_player(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        player = self._parse_json(self._search_regex(
            r'window\.__PRELOADED_STATE__\s*=\s*({.+})', webpage,
            'player', default='{}'), video_id, transform_source=js_to_json)
        video_info = player['player']['nowPlaying']

        return (
            video_id,
            player,
            video_info,
        )

    def _real_extract(self, url):
        video_id, player, video_info = self._extract_player(url)
        return {
            'url': video_info['mediaurl'] or video_info['mediaurl_mp3'],
            'id': video_id,
            'title': video_info['title'],
            'thumbnail': video_info.get('imageurl_square') or video_info.get('imageurl'),
            'timestamp': parse_iso8601(video_info.get('starttime'), ' '),
            'duration': int_or_none(video_info.get('duration')),
            'channel': player.get('listenApi').get('data').get('stationName'),
        }


class RadioplayPodcastIE(RadioplayIE):
    _VALID_URL = r'https?://(?:www\.)?radioplay\.(?:se|no)/podcast/[^/]+/[^/]+/(?P<id>\d+)'

    _TEST = {
        'url': 'https://radioplay.se/podcast/lilla-my/lyssna/2001126',
        'info_dict': {
            'id': '2001126',
            'ext': 'mp3',
            'title': 'Kaktus till läraren',
            'description': 'Lilla My ska köpa en "blomma" till sin lärare.',
            'timestamp': 1549898100,
            'upload_date': '20190211',
        },
    }

    def _real_extract(self, url):
        video_id, player, video_info = self._extract_player(url)

        return {
            'url': video_info['PodcastExtMediaUrl'],
            'id': video_id,
            'title': video_info['PodcastTitle'],
            'description': video_info.get('PodcastDescription'),
            'thumbnail': video_info.get('PodcastImageUrl'),
            'release_date': unified_strdate(video_info.get('PodcastPublishDate')),
            'timestamp': parse_iso8601(video_info.get('PodcastPublishDate'), ' '),
            'duration': int_or_none(video_info.get('PodcastDuration')),
            'channel': player.get('podcastsApi').get('data').get('channel').get('PodcastChannelTitle'),
        }
