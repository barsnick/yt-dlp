# coding: utf-8
from __future__ import unicode_literals

from ..utils import int_or_none, js_to_json, parse_iso8601, unified_strdate
from .common import InfoExtractor
import re


class RadioplayRedirectIE(InfoExtractor):
    _VALID_URL = r'https?://(?:live|lytte)\.radioplay\.(?:se|no|dk)/(?P<id>\d+)'

    _TEST = {
        'url': 'https://lytte.radioplay.no/10279674',
        'info_dict': {
            'id': '2035659',
            'ext': 'mp3',
            'title': 'Best of Høsten 2020',
            'description': 'md5:701b09a2bcf9a75b6bfd8a27f359dcfa',
            'timestamp': 1603429200,
            'upload_date': '20201023',
            'release_date': '20201023',
            'channel': 'Siri og de gode hjelperne',
            'thumbnail': r're:https?://.*',
            'duration': 4182,
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        url = self._search_regex(
            r'desktopUrl\s*:\s*\'([^\']+)\'', webpage,
            'redirect', video_id)
        return self.url_result(url)


class RadioplayIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?radioplay\.(?:se|no|dk)/[^/]+/spiller/(?P<id>\d+)/?'

    _TEST = {
        'url': 'https://radioplay.no/radio-rock/spiller/178851646/',
        'info_dict': {
            'id': '178851646',
            'ext': 'mp3',
            'title': 'Stå Opp!',
            'timestamp': 1630141200,
            'upload_date': '20210828',
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


class RadioplayPodcastRedirectIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?radioplay\.(?:se|no|dk)/podcast/[^/]+/id-(?P<id>\d+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        for url in re.findall(r'<div[^>]* data-test="audible-now-playing-button-container"[^>]*>.*<a href="([^"]+)"', webpage):
            return self.url_result(url)


class RadioplayPodcastIE(RadioplayIE):
    _VALID_URL = r'https?://(?:www\.)?radioplay\.(?:se|no|dk)/podcast/[^/]+/[^/]+/(?P<id>\d+)'

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
