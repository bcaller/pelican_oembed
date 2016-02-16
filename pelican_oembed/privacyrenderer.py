# Copyright (c) 2016 Ben Caller

import os

import errno
import requests
from pyembed.core.render import DefaultRenderer
from re import sub

OEMBED_IMG = '<img class="oembed-preview" data-content="%(encoded_html)s" ' \
             'title="%(encoded_title)s" src="%(thumbnail_url)s" width="%(thumbnail_width)s" ' \
             'height="%(thumbnail_height)s" />'


class PrivacyRenderer(DefaultRenderer):
    """Replaces external video embedding with a clickable image preview."""

    def __init__(self, config):
        super(PrivacyRenderer, self).__init__()
        self.config = config

        video_format = config.get("OEMBED_VIDEO_FORMAT")
        if video_format:
            if type(video_format) is str:
                self.video_format = lambda params: video_format % params
            elif hasattr(video_format, '__call__'):
                self.video_format = video_format
        else:
            self.video_format = lambda params: OEMBED_IMG % params

    def render(self, content_url, response):
        params = dict(response if type(response) is dict else response.__dict__)
        self._save_to_cache(content_url, params)

        params['content_url'] = content_url

        if params['type'] == 'video' and 'thumbnail_url' in params:
            params['thumbnail_url'] = self._save_thumbnail(params['thumbnail_url'])
            params['encoded_html'] = params['html'].replace('"', '&quot;')
            if 'title' in params:
                params['encoded_title'] = params['title'].replace('"', '&quot;')
            return self.video_format(params)
        else:
            # Pass through to super class from pyembed_markdown package
            return self.TEMPLATES[params['type']] % params

    def _save_thumbnail(self, url):
        """Downloads the thumbnail and saves it. Returns the new thumbnail url."""

        save_path = self.config.get('OEMBED_THUMBNAIL_SAVE_AS')
        if not save_path:
            return url
        filename = sub(r'[*."/\\\[\]:;|=,]', '_', os.path.splitext(url[url.find('://') + 3:])[0])
        filename += os.path.splitext(url)[1]
        thumbnail_path = os.path.join(self.config.get('OUTPUT_PATH'), save_path % filename)

        if thumbnail_path is not None:
            self._make_directories()
            try:
                with open(thumbnail_path, 'x+b') as f:
                    r = requests.get(url, stream=True)
                    if r.status_code == 200:
                        for chunk in r:
                            f.write(chunk)
                    else:
                        raise Exception("Bad HTTP request for thumbnail")
            except OSError as e:
                if e.errno != errno.EEXIST:  # Thumbnail exists already, so no need to re-download
                    raise e
            return self.config.get('OEMBED_THUMBNAIL_URL') % filename
        else:
            return url

    def _save_to_cache(self, url, params):
        if self.config.get('_OEMBED_CACHE') is not None:
            self.config['_OEMBED_CACHE'][url] = params.copy()

    def _make_directories(self):
        thumbnail_dir = os.path.join(self.config.get('OUTPUT_PATH'), self.config.get('OEMBED_THUMBNAIL_SAVE_AS') % "")
        try:
            os.makedirs(thumbnail_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:  # Directory already exists :)
                raise
