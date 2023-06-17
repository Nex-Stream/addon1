# -*- coding: utf-8 -*-
import urllib.parse
import ast
import xbmc

from core import httptools, support, filetools
from platformcode import logger, config
from concurrent import futures
from urllib.parse import urlparse

vttsupport = False if int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0]) < 20 else True


def test_video_exists(page_url):
    global iframe
    global iframeParams

    iframe = support.scrapertools.decodeHtmlentities(support.match(page_url, patron='<iframe [^>]+src="([^"]+)').match)
    iframeParams = support.match(iframe, patron='window\.masterPlaylistParams\s=\s({.*?})').match

    if not iframeParams:
        return 'StreamingCommunity', 'Prossimamente'

    return True, ""


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    urls = list()
    subs = list()
    composed_subs = list()
    local_subs = list()
    video_urls = list()

    scws_id = urlparse(iframe).path.split('/')[-1]
    masterPlaylistParams = ast.literal_eval(iframeParams)
    url = 'https://scws.work/v2/playlist/{}?{}&n=1'.format(scws_id, urllib.parse.urlencode(masterPlaylistParams))

    info = support.match(url, patron=r'LANGUAGE="([^"]+)",\s*URI="([^"]+)|RESOLUTION=\d+x(\d+).*?(http[^"\s]+)').matches

    if info:
        for lang, sub, res, url in info:
            if sub:
                if lang == 'auto': lang = 'ita-forced'
                subs.append([lang, sub])
            elif res != '1080':
                urls.append([res, url])

        if subs:
            with futures.ThreadPoolExecutor() as executor:
                itlist = [executor.submit(subs_downloader, n, s) for n, s in enumerate(subs)]
                for res in futures.as_completed(itlist):
                    if res.result():
                        composed_subs.append(res.result())

            local_subs = [s[1] for s in sorted(composed_subs, key=lambda n: n[0])]

            video_urls = [['m3u [{}]'.format(res), url, 0, local_subs] for res, url in urls]
    else:
        video_urls = [['hls', url]]

    return video_urls


def subs_downloader(n, s):
    lang, url = s

    match = support.match(url, patron=r'(http[^\s\n]+)').match

    if match:
        data = httptools.downloadpage(match).data

        if lang == 'auto': lang = 'ita-forced'

        sub = config.get_temp_file('{}.{}'.format(lang, 'vtt' if vttsupport else 'str'))

        filetools.write(sub, data if vttsupport else support.vttToSrt(data))
        return n, sub
