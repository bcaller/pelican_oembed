# Copyright (c) 2016 Ben Caller
import gzip
import json

from pelican import signals

from .cachingmarkdownextension import CachingPyEmbedMarkdownExtension
from .privacyrenderer import PrivacyRenderer


def add_md_ext(pelican):
    # Saving thumbnails locally
    thumbnail_save_as = pelican.settings.get('OEMBED_THUMBNAIL_SAVE_AS')
    thumbnail_url = pelican.settings.get('OEMBED_THUMBNAIL_URL')
    if thumbnail_save_as is not None and thumbnail_url is None:
        pelican.settings['OEMBED_THUMBNAIL_URL'] = '/' + thumbnail_save_as

    # Caching oembed lookups
    cache = None
    if 'OEMBED_CACHE_FILE' in pelican.settings:
        try:
            with gzip.open(pelican.settings.get('OEMBED_CACHE_FILE'), 'rt') as json_file:
                cache = pelican.settings['_OEMBED_CACHE'] = json.load(json_file)
        except (FileNotFoundError, ValueError, OSError):
            cache = pelican.settings['_OEMBED_CACHE'] = dict()

    # Add extension
    md_ext = pelican.settings.get('MD_EXTENSIONS')
    markdown_extension_class = CachingPyEmbedMarkdownExtension
    extension = markdown_extension_class(renderer=PrivacyRenderer(pelican.settings), cache=cache)
    if not md_ext:
        pelican.settings['MD_EXTENSIONS'] = [extension]
    elif not any([isinstance(ext, markdown_extension_class) for ext in md_ext]):
        md_ext.append(extension)
        pelican.settings['MD_EXTENSIONS'] = md_ext


def save_cache(pelican):
    if 'OEMBED_CACHE_FILE' in pelican.settings:
        with gzip.open(pelican.settings.get('OEMBED_CACHE_FILE'), 'wt') as json_file:
            json.dump(pelican.settings.get('_OEMBED_CACHE'), json_file)


def register():
    signals.initialized.connect(add_md_ext)
    signals.finalized.connect(save_cache)
